class Chunker:

    def __init__(self, size=1200, overlap=200):
        self.size=size
        self.overlap=overlap

    def split(self,text):

        if not text:
            return []

        chunks=[]
        i=0

        while i<len(text):

            chunks.append(text[i:i+self.size])

            i+=self.size-self.overlap

        return chunks
