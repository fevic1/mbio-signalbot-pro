from pathlib import Path
from pypdf import PdfReader

class PDFParser:

    def parse(self,path):

        reader=PdfReader(path)

        pages=[]

        for page in reader.pages:
            pages.append(
                page.extract_text() or ""
            )

        return "\n".join(pages)
