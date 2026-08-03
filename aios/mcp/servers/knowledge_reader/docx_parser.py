from docx import Document

class DocxParser:

    def parse(self,path):

        doc=Document(path)

        return "\n".join(
            p.text
            for p in doc.paragraphs
        )
