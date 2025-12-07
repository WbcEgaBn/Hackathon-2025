# notifications/email_renderer.py

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from datetime import date

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=select_autoescape(["html", "xml"]),
)

template = env.get_template("simple_digest.html")


def render_digest(user, items):
    today_str = date.today().strftime("%B %d, %Y")

    html = template.render(
        user=user,
        items=items,
        date=today_str,
    )

    debug_path = Path("last_digest_debug.html")
    debug_path.write_text(html, encoding="utf-8")

    return html
