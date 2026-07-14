"""Factuurberekeningen en de levenscyclus concept → definitief → betaald.

Bedragen zijn integers in centen. Berekening volgt het origineel:
regels (aantal × stukprijs excl. btw), optionele korting als percentage op
het subtotaal, btw per tariefgroep over het bedrag ná korting.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from .ledger import Boekregel, BoekingsFout, maak_journaalpost
from .models import Factuur, Instellingen


def _rond(bedrag: Decimal) -> int:
    """Rond een Decimal-bedrag in centen af naar een integer (half-up)."""
    return int(bedrag.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


@dataclass
class FactuurTotalen:
    subtotaal: int = 0
    korting: int = 0
    totaal_excl: int = 0
    btw_per_pct: dict[Decimal, int] = field(default_factory=dict)  # pct -> btw-bedrag
    btw_totaal: int = 0
    totaal_incl: int = 0


def bereken_totalen(factuur: Factuur) -> FactuurTotalen:
    t = FactuurTotalen()
    korting_factor = Decimal(1) - Decimal(str(factuur.korting_pct or 0)) / Decimal(100)

    per_pct_excl: dict[Decimal, Decimal] = {}
    for regel in factuur.regels:
        regel_totaal = Decimal(str(regel.aantal)) * Decimal(regel.bedrag_cents)
        pct = Decimal(str(regel.btw_tarief.percentage)) if regel.btw_tarief else Decimal(0)
        per_pct_excl[pct] = per_pct_excl.get(pct, Decimal(0)) + regel_totaal

    t.subtotaal = _rond(sum(per_pct_excl.values(), Decimal(0)))
    for pct, groep in sorted(per_pct_excl.items()):
        groep_na_korting = groep * korting_factor
        btw = _rond(groep_na_korting * pct / Decimal(100))
        if pct > 0:
            t.btw_per_pct[pct] = t.btw_per_pct.get(pct, 0) + btw
        t.totaal_excl += _rond(groep_na_korting)
        t.btw_totaal += btw
    t.korting = t.subtotaal - t.totaal_excl
    t.totaal_incl = t.totaal_excl + t.btw_totaal
    return t


def volgend_factuurnummer(db: Session, factuurdatum: date) -> str:
    """Geeft het volgende opeenvolgende nummer (formaat jaar-XXXX, rouleert per jaar)."""
    instellingen = db.query(Instellingen).one()
    if instellingen.factuur_jaar != factuurdatum.year:
        instellingen.factuur_jaar = factuurdatum.year
        instellingen.factuur_volgnummer = 1
    nummer = f"{instellingen.factuur_jaar}-{instellingen.factuur_volgnummer:04d}"
    instellingen.factuur_volgnummer += 1
    return nummer


def maak_definitief(db: Session, factuur: Factuur) -> None:
    """Kent het factuurnummer toe en journaliseert in het verkoopboek.

    Na deze stap is de factuur onveranderlijk (correcties via creditfactuur).
    """
    if factuur.status != "concept":
        raise BoekingsFout("Alleen conceptfacturen kunnen definitief worden gemaakt")
    if factuur.relatie is None:
        raise BoekingsFout("Kies eerst een klant")
    if not factuur.regels:
        raise BoekingsFout("Een factuur heeft minimaal één regel nodig")

    totalen = bereken_totalen(factuur)
    factuur.nummer = volgend_factuurnummer(db, factuur.factuurdatum)

    regels = [
        Boekregel("Debiteuren", debet_cents=totalen.totaal_incl, relatie_id=factuur.relatie_id),
        Boekregel("Omzet", credit_cents=totalen.totaal_excl, relatie_id=factuur.relatie_id),
    ]
    if totalen.btw_totaal:
        regels.append(Boekregel("Te betalen btw", credit_cents=totalen.btw_totaal))
    maak_journaalpost(
        db,
        datum=factuur.factuurdatum,
        dagboek="verkoopboek",
        omschrijving=f"{factuur.relatie.naam} {factuur.nummer}",
        regels=regels,
        factuur_id=factuur.id,
    )
    factuur.status = "definitief"
    db.flush()


def registreer_betaling(db: Session, factuur: Factuur, datum: date) -> None:
    """Boekt de ontvangst op de bank en zet de factuur op betaald."""
    if factuur.status != "definitief":
        raise BoekingsFout("Alleen definitieve, openstaande facturen kunnen op betaald")
    totalen = bereken_totalen(factuur)
    maak_journaalpost(
        db,
        datum=datum,
        dagboek="bank",
        omschrijving=f"Betaling {factuur.nummer} {factuur.relatie.naam}",
        regels=[
            Boekregel("Bank", debet_cents=totalen.totaal_incl),
            Boekregel("Debiteuren", credit_cents=totalen.totaal_incl, relatie_id=factuur.relatie_id),
        ],
        factuur_id=factuur.id,
    )
    factuur.status = "betaald"
    db.flush()
