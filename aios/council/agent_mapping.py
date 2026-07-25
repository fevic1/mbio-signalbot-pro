COUNCIL_AGENT_CAPABILITIES = {

    "architect": [
        "architecture_review",
        "system_design",
        "failure_analysis",
    ],

    "risk": [
        "risk_review",
        "exposure_analysis",
        "capital_protection",
    ],

    "skeptic": [
        "assumption_testing",
        "failure_detection",
    ],

    "verification": [
        "validation",
        "quality_control",
    ],
}


def capabilities_for(agent):

    return COUNCIL_AGENT_CAPABILITIES.get(
        agent,
        [],
    )
