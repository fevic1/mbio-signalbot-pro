class EvidenceFusion:

    def fuse(self, tool_results):

        fused = {
            "successful": [],
            "failed": [],
            "sources": [],
            "confidence": 0.0,
        }

        for result in tool_results:

            if result.get("success"):

                fused["successful"].append(result)

                fused["sources"].append(
                    result["server"]
                )

            else:

                fused["failed"].append(result)

        total = len(tool_results)

        if total:

            fused["confidence"] = round(
                len(fused["successful"]) / total,
                3,
            )

        return fused
