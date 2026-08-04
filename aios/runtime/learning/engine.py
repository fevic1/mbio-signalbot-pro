from dataclasses import dataclass


@dataclass(slots=True)
class LearningRecord:
    capability: str
    provider: str
    model: str
    success: bool
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    latency: float
    cost: float
    verification_score: float


class LearningEngine:

    def record(self, response):

        return LearningRecord(
            capability=response.metadata.get("capability",""),
            provider=response.provider,
            model=response.model,
            success=response.verification_passed,
            prompt_tokens=response.prompt_tokens,
            completion_tokens=response.completion_tokens,
            total_tokens=response.total_tokens,
            latency=response.total_latency,
            cost=response.estimated_cost,
            verification_score=response.verification_score,
        )
