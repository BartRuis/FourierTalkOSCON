from datetime import date

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..facturen_service import bereken_totalen
from ..ledger import saldo_van_categorie
from ..models import Categorie, Factuur, JournaalPost, JournaalRegel
from ..templating import render

router = APIRouter()

WINST_EN_VERLIES_TYPES = (
    "Opbrengsten",
    "Inkoopkosten en uitbesteed werk",
    "Overige bedrijfskosten",
    "Afschrijvingen",
    "Financiële baten en lasten",
)


def _wv_saldi(db: Session, jaar: int) -> tuple[list[tuple[str, int]], list[tuple[str, int]], int, int]:
    """Opbrengsten- en kostenposten (naam, cents) voor de W&V van een jaar."""
    opbrengsten: list[tuple[str, int]] = []
    kosten: list[tuple[str, int]] = []
    for categorie in db.query(Categorie).order_by(Categorie.naam).all():
        hoofdtype = categorie.type.split(" - ")[0]
        if hoofdtype not in WINST_EN_VERLIES_TYPES:
            continue
        saldo = saldo_van_categorie(db, categorie.naam, jaar)
        if saldo == 0:
            continue
        if hoofdtype == "Opbrengsten":
            opbrengsten.append((categorie.naam, -saldo))  # creditsaldo positief tonen
        else:
            kosten.append((categorie.naam, saldo))
    totaal_opbrengsten = sum(bedrag for _, bedrag in opbrengsten)
    totaal_kosten = sum(bedrag for _, bedrag in kosten)
    return opbrengsten, kosten, totaal_opbrengsten, totaal_kosten


@router.get("/", response_class=HTMLResponse)
def dashboard(db: Session = Depends(get_db)):
    jaar = date.today().year
    opbrengsten, kosten, totaal_opbrengsten, totaal_kosten = _wv_saldi(db, jaar)
    open_facturen = db.query(Factuur).filter(Factuur.status == "definitief").all()
    te_ontvangen = sum(bereken_totalen(f).totaal_incl for f in open_facturen)
    laatste_facturen = db.query(Factuur).order_by(Factuur.id.desc()).limit(5).all()
    return render(
        "dashboard.html",
        jaar=jaar,
        omzet=totaal_opbrengsten,
        kosten=totaal_kosten,
        winst=totaal_opbrengsten - totaal_kosten,
        te_ontvangen=te_ontvangen,
        banksaldo=saldo_van_categorie(db, "Bank"),
        btw_saldo=-saldo_van_categorie(db, "Te betalen btw", jaar) - saldo_van_categorie(db, "Te vorderen btw", jaar),
        laatste_facturen=[(f, bereken_totalen(f)) for f in laatste_facturen],
        actief="dashboard",
    )


@router.get("/mutaties", response_class=HTMLResponse)
def mutaties(jaar: int | None = None, db: Session = Depends(get_db)):
    jaar = jaar or date.today().year
    regels = (
        db.query(JournaalRegel)
        .join(JournaalPost)
        .filter(JournaalPost.jaar == jaar)
        .order_by(JournaalPost.datum.desc(), JournaalPost.id.desc(), JournaalRegel.id)
        .all()
    )
    jaren = sorted({j for (j,) in db.query(JournaalPost.jaar).distinct()} | {date.today().year}, reverse=True)
    return render("mutaties.html", regels=regels, jaar=jaar, jaren=jaren, actief="mutaties")


@router.get("/winst-en-verlies", response_class=HTMLResponse)
def winst_en_verlies(jaar: int | None = None, db: Session = Depends(get_db)):
    jaar = jaar or date.today().year
    opbrengsten, kosten, totaal_opbrengsten, totaal_kosten = _wv_saldi(db, jaar)
    jaren = sorted({j for (j,) in db.query(JournaalPost.jaar).distinct()} | {date.today().year}, reverse=True)
    return render(
        "winst_en_verlies.html",
        jaar=jaar, jaren=jaren,
        opbrengsten=opbrengsten, kosten=kosten,
        totaal_opbrengsten=totaal_opbrengsten, totaal_kosten=totaal_kosten,
        winst=totaal_opbrengsten - totaal_kosten,
        actief="winst-en-verlies",
    )
