"""De double-entry kern: alle boekingen lopen via maak_journaalpost().

Elke journaalpost moet in balans zijn (som debet == som credit); anders
wordt de boeking geweigerd. Rapportages (mutaties, W&V, balans, btw) zijn
afleidingen van deze posten.
"""

from dataclasses import dataclass
from datetime import date

from sqlalchemy.orm import Session

from .models import Categorie, JournaalPost, JournaalRegel, Periode
from .seed import zorg_voor_periodes

DAGBOEKEN = ("verkoopboek", "inkopen", "bank", "memoriaal")


class BoekingsFout(Exception):
    pass


@dataclass
class Boekregel:
    categorie: str  # categorienaam uit het rekeningschema
    debet_cents: int = 0
    credit_cents: int = 0
    relatie_id: int | None = None


def maak_journaalpost(
    db: Session,
    datum: date,
    dagboek: str,
    omschrijving: str,
    regels: list[Boekregel],
    factuur_id: int | None = None,
    periode_nummer: int | None = None,
) -> JournaalPost:
    if dagboek not in DAGBOEKEN:
        raise BoekingsFout(f"Onbekend dagboek: {dagboek}")
    if not regels:
        raise BoekingsFout("Een journaalpost heeft minimaal één regel nodig")

    totaal_debet = sum(r.debet_cents for r in regels)
    totaal_credit = sum(r.credit_cents for r in regels)
    if any(r.debet_cents < 0 or r.credit_cents < 0 for r in regels):
        raise BoekingsFout("Negatieve bedragen zijn niet toegestaan; draai debet en credit om")
    if totaal_debet != totaal_credit:
        raise BoekingsFout(
            f"Journaalpost is niet in balans: debet {totaal_debet} != credit {totaal_credit}"
        )

    nummer = periode_nummer if periode_nummer is not None else datum.month
    zorg_voor_periodes(db, datum.year)
    periode = (
        db.query(Periode)
        .filter(Periode.jaar == datum.year, Periode.nummer == nummer)
        .one()
    )
    if not periode.open:
        raise BoekingsFout(f"Periode {periode.jaar}-{periode.nummer} is gesloten")

    post = JournaalPost(
        datum=datum,
        dagboek=dagboek,
        jaar=datum.year,
        periode_nummer=nummer,
        omschrijving=omschrijving,
        factuur_id=factuur_id,
    )
    for r in regels:
        categorie = db.query(Categorie).filter(Categorie.naam == r.categorie).one_or_none()
        if categorie is None:
            raise BoekingsFout(f"Onbekende categorie: {r.categorie}")
        post.regels.append(
            JournaalRegel(
                categorie=categorie,
                debet_cents=r.debet_cents,
                credit_cents=r.credit_cents,
                relatie_id=r.relatie_id,
            )
        )
    db.add(post)
    db.flush()
    return post


def saldo_van_categorie(db: Session, categorie_naam: str, jaar: int | None = None) -> int:
    """Saldo in cents (debet positief) van een categorie, optioneel beperkt tot een jaar."""
    query = (
        db.query(JournaalRegel)
        .join(JournaalPost)
        .join(Categorie)
        .filter(Categorie.naam == categorie_naam)
    )
    if jaar is not None:
        query = query.filter(JournaalPost.jaar == jaar)
    regels = query.all()
    return sum(r.debet_cents - r.credit_cents for r in regels)
