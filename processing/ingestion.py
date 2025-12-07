# app/processing/ingestion.py

from datetime import date

def fetch_new_meetings():
    """
    Hackathon-friendly stub:
    Returns a list of local PDFs you want to ingest.
    In production: scrape Legistar for new agenda URLs.
    """

    return [
        {
            "date": date(2025, 1, 15),
            "type": "City Council",
            "pdf_path": "sample_data/agenda1.pdf",
        },
        {
            "date": date(2025, 1, 29),
            "type": "Planning Commission",
            "pdf_path": "sample_data/agenda2.pdf",
        }
    ]
