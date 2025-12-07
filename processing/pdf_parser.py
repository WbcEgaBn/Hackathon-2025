import pdfplumber

def extract_text_from_pdf(path: str) -> str:
    lines = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                page_lines = [line.rstrip() for line in text.split("\n")]
                lines.extend(page_lines)
    return "\n".join(lines)
