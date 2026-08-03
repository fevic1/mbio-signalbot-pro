import wikipedia

class WikipediaClient:

    def search(self, query):
        return wikipedia.search(query)

    def summary(self, title):
        return wikipedia.summary(title)

    def page(self, title):
        return wikipedia.page(title)
