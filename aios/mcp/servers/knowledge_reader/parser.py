from pathlib import Path
import json
import csv

from .pdf_parser import PDFParser
from .docx_parser import DocxParser

pdf=PDFParser()
docx=DocxParser()

class Parser:

    def parse(self,path):

        path=Path(path)

        suffix=path.suffix.lower()

        if suffix==".pdf":
            return pdf.parse(path)

        if suffix==".docx":
            return docx.parse(path)

        if suffix in [".txt",".md",".html"]:
            return path.read_text(
                errors="ignore"
            )

        if suffix==".json":
            return json.dumps(
                json.loads(path.read_text()),
                indent=2
            )

        if suffix==".csv":

            rows=[]

            with open(path,newline="") as f:
                for row in csv.reader(f):
                    rows.append(",".join(row))

            return "\n".join(rows)

        raise ValueError(
            f"Unsupported file type: {suffix}"
        )
