import pdfplumber

def extract_text_from_pdf(path: str) -> str:
    """
    Extract clean, reliable text for agendas that are well-structured.
    We extract text line-by-line with pdfplumber to preserve structure.
    """
    lines = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                # Keep each page intact but normalize whitespace
                page_lines = [line.rstrip() for line in text.split("\n")]
                lines.extend(page_lines)
    return "\n".join(lines)
