"""Factuur-PDF via een Jinja2 HTML-template en WeasyPrint."""

from datetime import timedelta

from weasyprint import HTML

from .facturen_service import bereken_totalen
from .models import Factuur, Instellingen
from .templating import templates


def factuur_pdf(factuur: Factuur, instellingen: Instellingen) -> bytes:
    template = templates.get_template("facturen/pdf.html")
    html = template.render(
        factuur=factuur,
        instellingen=instellingen,
        totalen=bereken_totalen(factuur),
        vervaltermijn=timedelta(days=instellingen.betaaltermijn_dagen),
    )
    return HTML(string=html).write_pdf()
