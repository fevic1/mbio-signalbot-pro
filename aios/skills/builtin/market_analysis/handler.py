
class MarketAnalysisHandler:

    def execute(self, context):

        context.metadata["skill"] = (
            "market_analysis"
        )

        return context
