"""Gedeelde Jinja2-omgeving met euro- en datumfilters."""

import os
from datetime import date

from jinja2 import Environment, FileSystemLoader

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def euro(cents: int | None) -> str:
    """Formatteert centen als Nederlands bedrag: 1234567 -> '12.345,67'."""
    if cents is None:
        cents = 0
    negatief = cents < 0
    cents = abs(cents)
    euros, rest = divmod(cents, 100)
    tekst = f"{euros:,}".replace(",", ".") + f",{rest:02d}"
    return ("-" if negatief else "") + tekst


def datum_nl(waarde: date | None) -> str:
    return waarde.strftime("%d-%m-%Y") if waarde else ""


def pct(waarde) -> str:
    """Percentage zonder overbodige nullen: 10.00 -> '10', 10.50 -> '10,5'."""
    tekst = f"{float(waarde or 0):f}".rstrip("0").rstrip(".")
    return tekst.replace(".", ",")


templates = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=True)
templates.filters["euro"] = euro
templates.filters["datum"] = datum_nl
templates.filters["pct"] = pct


def render(naam: str, **context) -> str:
    return templates.get_template(naam).render(**context)
