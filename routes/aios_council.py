import asyncio
import json
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Request

from aios.capabilities.executor import CapabilityExecutor
from aios.capabilities.request import CapabilityRequest


logger = logging.getLogger(__name__)

router = APIRouter()


def _system(request):
    return request.app.state.aios


def _normalize_content(result):
    content = result.get("content", "")

    if isinstance(content, dict):
        content = (
            content.get("summary")
            or content.get("message")
            or content.get("reasoning")
            or content.get("response")
            or json.dumps(content, indent=2, default=str)
        )

    if isinstance(content, list):
        content = json.dumps(content, indent=2, default=str)

    return str(content or "").strip()


async def _agent_response(
    system,
    review,
    agent,
    human_message,
):
    role_prompts = {
        "architect": (
            "You are the AIOS Council Architect. Analyze root cause, "
            "affected components, architecture impact, and propose a "
            "minimal reversible solution."
        ),
        "risk": (
            "You are the AIOS Council Risk Agent. Identify safety, "
            "security, regression, operational, and rollback risks."
        ),
        "skeptic": (
            "You are the AIOS Council Skeptic. Challenge assumptions, "
            "identify missing evidence, and present credible alternatives."
        ),
        "verification": (
            "You are the AIOS Council Verification Agent. Examine the "
            "available evidence, distinguish verified facts from claims, "
            "and specify the exact tests required."
        ),
    }

    discussion = review.get("discussion", [])[-20:]

    prompt = (
        role_prompts[agent]
        + "\n\nCouncil issue:\n"
        + review.get("title", "")
        + "\n"
        + review.get("description", "")
        + "\n\nEvidence:\n"
        + json.dumps(
            review.get("evidence", []),
            indent=2,
            default=str,
        )
        + "\n\nRecent Council discussion:\n"
        + json.dumps(
            discussion,
            indent=2,
            default=str,
        )
        + "\n\nHuman inquiry:\n"
        + human_message
        + "\n\nGive a decision-ready response in no more than 140 words. "
          "Lead with your conclusion. Then state the next step, principal "
          "risk or objection, and any missing evidence. Use natural, "
          "professional prose; do not return JSON or expose chain-of-thought. "
          "Do not claim a change was applied."
    )

    request = CapabilityRequest(
        capability="reasoning",
        context={
            "message": prompt,
            "target_agent": agent,
            "aios_mode": "council_deliberation",
        },
    )

    result = await CapabilityExecutor(system).execute(request)

    return {
        "agent": agent,
        "content": _normalize_content(result),
        "confidence": result.get("confidence"),
        "provider": result.get("provider"),
        "model": result.get("model"),
        "success": result.get("success", True),
    }


async def _run_council_turn(
    system,
    store,
    review_id,
    human_message,
    target="all",
):
    review = store.get(review_id)

    if review is None:
        return

    available_agents = (
        "architect",
        "risk",
        "skeptic",
        "verification",
    )

    agents = (
        (target,)
        if target in available_agents
        else available_agents
    )

    try:
        for agent in agents:
            store.set_agent_state(
                review_id,
                agent,
                "reviewing",
            )

        responses = await asyncio.gather(
            *[
                _agent_response(
                    system,
                    review,
                    agent,
                    human_message,
                )
                for agent in agents
            ],
            return_exceptions=True,
        )

        valid_responses = []

        for agent, response in zip(agents, responses):
            if isinstance(response, Exception):
                logger.exception(
                    "Council agent failed: %s",
                    agent,
                    exc_info=response,
                )
                store.set_agent_state(
                    review_id,
                    agent,
                    "failed",
                )
                store.add_message(
                    review_id,
                    actor=agent,
                    role="system",
                    target="council",
                    message=(
                        "Agent response unavailable: "
                        + str(response)
                    ),
                )
                continue

            valid_responses.append(response)

            metadata = " · ".join(
                item
                for item in (
                    response.get("provider"),
                    response.get("model"),
                )
                if item
            )

            content = response["content"]

            if metadata:
                content += f"\n\nModel: {metadata}"

            store.add_message(
                review_id,
                actor=agent,
                role="agent",
                target="human",
                message=content,
                confidence=response.get("confidence"),
            )

        store.set_agent_state(
            review_id,
            "chair",
            "synthesizing",
        )

        current = store.get(review_id)

        synthesis_prompt = (
            "You are the AIOS Council Chair. Write a decision-ready summary "
            "in no more than 170 words. Lead with the recommendation. Cover "
            "only material agreement, disagreement, unresolved risk, evidence "
            "quality, and the exact human decision required. Use natural "
            "professional prose without JSON or generic AI phrasing. Human "
            "approval is still required and no action has been executed.\n\n"
            + json.dumps(
                current.get("discussion", []),
                indent=2,
                default=str,
            )
        )

        synthesis_result = await CapabilityExecutor(
            system
        ).execute(
            CapabilityRequest(
                capability="reasoning",
                context={
                    "message": synthesis_prompt,
                    "target_agent": "council_chair",
                    "aios_mode": "council_synthesis",
                },
            )
        )

        store.set_synthesis(
            review_id,
            summary=_normalize_content(
                synthesis_result
            ),
            recommendation="await_human_decision",
        )

    except Exception:
        logger.exception(
            "Council deliberation failed: review=%s",
            review_id,
        )
        store.set_agent_state(
            review_id,
            "chair",
            "failed",
        )


def _store(request):
    system = request.app.state.aios

    if isinstance(system, dict):
        services = system
    else:
        services = getattr(system, "services", {}) or {}

    store = services.get("council_review_store")

    if store is None:
        raise HTTPException(
            status_code=503,
            detail="Council review store unavailable",
        )

    return store


@router.get("/aios/council/reviews")
async def list_reviews(request: Request):
    store = _store(request)
    return {
        "reviews": store.all(),
        "pending": len(store.pending()),
        "unread": store.unread_count(),
    }


@router.get("/aios/council/reviews/{review_id}")
async def get_review(review_id: str, request: Request):
    review = _store(request).get(review_id)

    if review is None:
        raise HTTPException(404, "Council review not found")

    return {"review": review}


@router.post("/aios/council/reviews")
async def create_review(request: Request, payload: dict):
    title = str(payload.get("title", "")).strip()
    description = str(
        payload.get("description", "")
    ).strip()

    if not title or not description:
        raise HTTPException(
            400,
            "title and description are required",
        )

    review = _store(request).create(
        title=title,
        description=description,
        severity=payload.get("severity", "medium"),
        source=payload.get("source", "human"),
        evidence=payload.get("evidence", []),
        session=payload.get("session"),
    )

    return {"review": review}


@router.post(
    "/aios/council/reviews/{review_id}/discussion"
)
async def add_discussion(
    review_id: str,
    request: Request,
    payload: dict,
):
    message = str(payload.get("message", "")).strip()

    if not message:
        raise HTTPException(400, "message is required")

    review = _store(request).add_message(
        review_id=review_id,
        actor=payload.get("actor", "operator"),
        role=payload.get("role", "human"),
        target=payload.get("target", "all"),
        message=message,
        confidence=payload.get("confidence"),
        evidence=payload.get("evidence", []),
    )

    if review is None:
        raise HTTPException(404, "Council review not found")

    return {"review": review}


@router.post(
    "/aios/council/reviews/{review_id}/ask"
)
async def ask_council(
    review_id: str,
    request: Request,
    background_tasks: BackgroundTasks,
    payload: dict,
):
    store = _store(request)
    review = store.get(review_id)

    if review is None:
        raise HTTPException(404, "Council review not found")

    message = str(payload.get("message", "")).strip()
    target = str(payload.get("target", "all")).strip()

    if not message:
        raise HTTPException(400, "message is required")

    store.add_message(
        review_id=review_id,
        actor=payload.get("actor", "operator"),
        role="human",
        target=target,
        message=message,
    )

    background_tasks.add_task(
        _run_council_turn,
        _system(request),
        store,
        review_id,
        message,
        target,
    )

    return {
        "accepted": True,
        "review_id": review_id,
        "status": "deliberating",
    }


@router.post(
    "/aios/council/reviews/{review_id}/synthesis"
)
async def add_synthesis(
    review_id: str,
    request: Request,
    payload: dict,
):
    summary = str(payload.get("summary", "")).strip()

    if not summary:
        raise HTTPException(400, "summary is required")

    review = _store(request).set_synthesis(
        review_id=review_id,
        summary=summary,
        agreements=payload.get("agreements", []),
        disagreements=payload.get("disagreements", []),
        risks=payload.get("risks", []),
        recommendation=payload.get("recommendation"),
    )

    if review is None:
        raise HTTPException(404, "Council review not found")

    return {"review": review}


@router.post(
    "/aios/council/reviews/{review_id}/decision"
)
async def decide_review(
    review_id: str,
    request: Request,
    payload: dict,
):
    try:
        review = _store(request).decide(
            review_id=review_id,
            decision=str(
                payload.get("decision", "")
            ).lower(),
            actor=payload.get("actor", "human"),
            reason=payload.get("reason", ""),
        )
    except ValueError as error:
        raise HTTPException(409, str(error)) from error

    if review is None:
        raise HTTPException(404, "Council review not found")

    return {
        "review": review,
        "execution_authorized": False,
        "message": (
            "Decision recorded. No code or operational "
            "action was executed."
        ),
    }


@router.post(
    "/aios/council/reviews/{review_id}/read"
)
async def mark_read(review_id: str, request: Request):
    review = _store(request).mark_read(review_id)

    if review is None:
        raise HTTPException(404, "Council review not found")

    return {"review": review}
