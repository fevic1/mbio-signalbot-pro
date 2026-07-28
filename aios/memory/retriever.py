from aios.core.identifiable import Identifiable

class MemoryRetriever(Identifiable):


    def __init__(
        self,
        index,
    ):

        self.index = index



    def search(
        self,
        keyword,
    ):

        keyword = keyword.lower()


        results = []


        for item in self.index.all():

            content = str(
                item["data"]
            ).lower()


            if keyword in content:

                results.append(
                    item
                )


        return results



    def by_category(
        self,
        category,
    ):

        return [

            item

            for item in self.index.all()

            if item["category"]
            ==
            category

        ]
