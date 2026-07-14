from datetime import date
from decimal import Decimal

import pytest

from app.facturen_service import bereken_totalen, maak_definitief, registreer_betaling
from app.ledger import BoekingsFout, saldo_van_categorie
from app.models import BtwTarief, Factuur, FactuurRegel, JournaalPost, Relatie


def _tarief(db, omschrijving="21%", rubriek="1a"):
    return db.query(BtwTarief).filter_by(omschrijving=omschrijving, rubriek=rubriek).one()


def _factuur_voorbeeld(db):
    """De offerte uit de Knab-screenshots: 5 regels, 10% korting, 21% btw."""
    relatie = Relatie(naam="Thomassen Energy B.V.")
    db.add(relatie)
    db.flush()
    factuur = Factuur(factuurdatum=date(2026, 7, 14), relatie_id=relatie.id, korting_pct=Decimal(10))
    hoog = _tarief(db)
    for omschrijving, aantal, stukprijs in [
        ("HELIOS testcampagne on-site support", 140, 15000),
        ("Post-processing and reporting", 240, 13000),
        ("Attending HELIOS meetings", 30, 13000),
        ("Accomodation", 7, 30000),
        ("Travel", 1, 50000),
    ]:
        factuur.regels.append(
            FactuurRegel(omschrijving=omschrijving, aantal=aantal, bedrag_cents=stukprijs, btw_tarief_id=hoog.id)
        )
    db.add(factuur)
    db.flush()
    return factuur


def test_totalen_komen_overeen_met_knab_voorbeeld(db):
    totalen = bereken_totalen(_factuur_voorbeeld(db))
    assert totalen.subtotaal == 5870000  # € 58.700,00
    assert totalen.korting == 587000  # € 5.870,00
    assert totalen.totaal_excl == 5283000  # € 52.830,00
    assert totalen.btw_totaal == 1109430  # € 11.094,30
    assert totalen.totaal_incl == 6392430  # € 63.924,30


def test_btw_per_tariefgroep(db):
    relatie = Relatie(naam="Test")
    db.add(relatie)
    db.flush()
    factuur = Factuur(factuurdatum=date(2026, 1, 1), relatie_id=relatie.id)
    factuur.regels.append(FactuurRegel(aantal=1, bedrag_cents=10000, btw_tarief_id=_tarief(db).id))
    factuur.regels.append(FactuurRegel(aantal=1, bedrag_cents=10000, btw_tarief_id=_tarief(db, "9%", "1b").id))
    db.add(factuur)
    db.flush()
    totalen = bereken_totalen(factuur)
    assert totalen.btw_per_pct == {Decimal(21): 2100, Decimal(9): 900}
    assert totalen.totaal_incl == 23000


def test_definitief_maken_journaliseert_en_nummert(db):
    factuur = _factuur_voorbeeld(db)
    maak_definitief(db, factuur)

    assert factuur.nummer == "2026-0001"
    assert factuur.status == "definitief"
    post = db.query(JournaalPost).filter_by(factuur_id=factuur.id, dagboek="verkoopboek").one()
    assert sum(r.debet_cents for r in post.regels) == sum(r.credit_cents for r in post.regels)
    assert saldo_van_categorie(db, "Debiteuren") == 6392430
    assert saldo_van_categorie(db, "Omzet") == -5283000
    assert saldo_van_categorie(db, "Te betalen btw") == -1109430


def test_nummering_is_opeenvolgend(db):
    eerste = _factuur_voorbeeld(db)
    tweede = _factuur_voorbeeld(db)
    maak_definitief(db, eerste)
    maak_definitief(db, tweede)
    assert (eerste.nummer, tweede.nummer) == ("2026-0001", "2026-0002")


def test_nummering_rouleert_per_jaar(db):
    factuur_2026 = _factuur_voorbeeld(db)
    maak_definitief(db, factuur_2026)
    factuur_2027 = _factuur_voorbeeld(db)
    factuur_2027.factuurdatum = date(2027, 1, 2)
    maak_definitief(db, factuur_2027)
    assert factuur_2027.nummer == "2027-0001"


def test_definitief_vereist_klant_en_regels(db):
    leeg = Factuur(factuurdatum=date(2026, 1, 1))
    db.add(leeg)
    db.flush()
    with pytest.raises(BoekingsFout, match="klant"):
        maak_definitief(db, leeg)


def test_definitieve_factuur_niet_nogmaals_definitief(db):
    factuur = _factuur_voorbeeld(db)
    maak_definitief(db, factuur)
    with pytest.raises(BoekingsFout):
        maak_definitief(db, factuur)


def test_betaling_boekt_bank_tegen_debiteuren(db):
    factuur = _factuur_voorbeeld(db)
    maak_definitief(db, factuur)
    registreer_betaling(db, factuur, date(2026, 7, 20))

    assert factuur.status == "betaald"
    assert saldo_van_categorie(db, "Debiteuren") == 0
    assert saldo_van_categorie(db, "Bank") == 6392430


def test_betaling_alleen_op_definitieve_factuur(db):
    factuur = _factuur_voorbeeld(db)
    with pytest.raises(BoekingsFout):
        registreer_betaling(db, factuur, date(2026, 7, 20))
