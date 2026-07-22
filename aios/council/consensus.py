class Consensus:

    def vote(self, report):

        return {
            "approved": (
                report["validator"]["valid"]
                and report["policy"]["allowed"]
            ),
            "confidence": report["critic"]["score"],
        }
