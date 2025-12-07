from datetime import date

def fetch_new_meetings():

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
