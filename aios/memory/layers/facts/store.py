from ..base import MemoryLayer


class FactsMemory(MemoryLayer):


    def save(
        self,
        data,
    ):

        return self.repository.save(
            data
        )



    def search(
        self,
        query,
    ):

        results = []

        for item in self.repository.all():

            if query.lower() in str(
                item.content
            ).lower():

                results.append(item)


        return results
