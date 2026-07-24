from .models import SpecialistAgent


CODING_TEAM = [

    SpecialistAgent(
        name="architect",
        role="Architect",
        domain="coding",
        capabilities=[
            "design",
            "architecture",
        ],
    ),

    SpecialistAgent(
        name="planner",
        role="Planner",
        domain="coding",
        capabilities=[
            "planning",
        ],
    ),

    SpecialistAgent(
        name="coder",
        role="Coder",
        domain="coding",
        capabilities=[
            "code",
            "implementation",
        ],
    ),

    SpecialistAgent(
        name="reviewer",
        role="Reviewer",
        domain="coding",
        capabilities=[
            "review",
        ],
    ),

    SpecialistAgent(
        name="tester",
        role="Tester",
        domain="coding",
        capabilities=[
            "verification",
            "testing",
        ],
    ),

    SpecialistAgent(
        name="security_auditor",
        role="Security Auditor",
        domain="coding",
        capabilities=[
            "security",
        ],
    ),

    SpecialistAgent(
        name="performance_optimizer",
        role="Performance Optimizer",
        domain="coding",
        capabilities=[
            "optimization",
        ],
    ),

    SpecialistAgent(
        name="documentation_writer",
        role="Documentation Writer",
        domain="coding",
        capabilities=[
            "documentation",
        ],
    ),
]


RESEARCH_TEAM = [
    SpecialistAgent(
        name="researcher",
        role="Researcher",
        domain="research",
        capabilities=["research"],
    ),

    SpecialistAgent(
        name="fact_checker",
        role="Fact Checker",
        domain="research",
        capabilities=["fact_check"],
    ),

    SpecialistAgent(
        name="skeptic",
        role="Skeptic",
        domain="research",
        capabilities=["challenge"],
    ),

    SpecialistAgent(
        name="verifier",
        role="Verifier",
        domain="research",
        capabilities=["verification"],
    ),

    SpecialistAgent(
        name="summarizer",
        role="Summarizer",
        domain="research",
        capabilities=["summarization"],
    ),
]
