import re


class SemanticSearch:


    def tokenize(
        self,
        text,
    ):

        return set(
            re.findall(
                r"\w+",
                text.lower(),
            )
        )



    def score(
        self,
        query,
        content,
    ):

        query_words = self.tokenize(
            query
        )

        content_words = self.tokenize(
            content
        )


        if not query_words:

            return 0


        matches = (
            query_words
            &
            content_words
        )


        return (
            len(matches)
            /
            len(query_words)
        )



    def rank(
        self,
        query,
        records,
    ):

        ranked = []


        for record in records:

            text = str(
                record.content
            )


            ranked.append(
                {
                    "record": record,
                    "score":
                        self.score(
                            query,
                            text,
                        ),
                }
            )


        return sorted(
            ranked,
            key=lambda x:
                x["score"],
            reverse=True,
        )
