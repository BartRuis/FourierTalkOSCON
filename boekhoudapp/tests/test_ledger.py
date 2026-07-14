from datetime import date

import pytest

from app.ledger import Boekregel, BoekingsFout, maak_journaalpost, saldo_van_categorie
from app.models import Periode


def test_journaalpost_moet_in_balans_zijn(db):
    with pytest.raises(BoekingsFout, match="niet in balans"):
        maak_journaalpost(
            db, date(2026, 7, 14), "memoriaal", "test",
            [Boekregel("Bank", debet_cents=100), Boekregel("Omzet", credit_cents=99)],
        )


def test_negatieve_bedragen_geweigerd(db):
    with pytest.raises(BoekingsFout, match="Negatieve"):
        maak_journaalpost(
            db, date(2026, 7, 14), "memoriaal", "test",
            [Boekregel("Bank", debet_cents=-100), Boekregel("Omzet", credit_cents=-100)],
        )


def test_onbekend_dagboek_geweigerd(db):
    with pytest.raises(BoekingsFout, match="dagboek"):
        maak_journaalpost(db, date(2026, 7, 14), "kasboek", "test", [Boekregel("Bank")])


def test_onbekende_categorie_geweigerd(db):
    with pytest.raises(BoekingsFout, match="categorie"):
        maak_journaalpost(
            db, date(2026, 7, 14), "memoriaal", "test",
            [Boekregel("Bestaat niet", debet_cents=1), Boekregel("Bank", credit_cents=1)],
        )


def test_balans_boeking_en_saldo(db):
    maak_journaalpost(
        db, date(2026, 7, 14), "bank", "storting",
        [Boekregel("Bank", debet_cents=250000), Boekregel("Privé-stortingen en -opnames", credit_cents=250000)],
    )
    assert saldo_van_categorie(db, "Bank") == 250000
    assert saldo_van_categorie(db, "Privé-stortingen en -opnames") == -250000


def test_periode_wordt_afgeleid_van_datum(db):
    post = maak_journaalpost(
        db, date(2026, 3, 5), "memoriaal", "test",
        [Boekregel("Bank", debet_cents=1), Boekregel("Omzet", credit_cents=1)],
    )
    assert (post.jaar, post.periode_nummer) == (2026, 3)


def test_boeken_in_gesloten_periode_geweigerd(db):
    periode = db.query(Periode).filter(Periode.jaar == date.today().year, Periode.nummer == 5).one()
    periode.open = False
    db.flush()
    with pytest.raises(BoekingsFout, match="gesloten"):
        maak_journaalpost(
            db, date(date.today().year, 5, 10), "memoriaal", "test",
            [Boekregel("Bank", debet_cents=1), Boekregel("Omzet", credit_cents=1)],
        )
