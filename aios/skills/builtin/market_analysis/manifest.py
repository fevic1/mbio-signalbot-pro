
from aios.skills.models import SkillManifest
from .handler import MarketAnalysisHandler


skill = SkillManifest(

    name="market_analysis",

    description=
        "Analyze market structure and signals",

    permission="research",

    handler=
        MarketAnalysisHandler(),

    input_schema={
        "symbol":"string",
        "timeframe":"string",
    },

    llm_instructions=
        "Analyze objectively and avoid assumptions."

)
