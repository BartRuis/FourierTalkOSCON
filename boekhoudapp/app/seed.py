"""Vult een lege database met het rekeningschema, btw-tarieven, periodes en instellingen."""

from datetime import date

from sqlalchemy.orm import Session

from .models import BtwTarief, Categorie, Instellingen, Periode

# Rekeningschema zoals geëxporteerd uit Knab Boekhouden / DigiBoox (bijlage A van het plan).
CATEGORIEEN = [
    ("Afschrijving auto's", "Afschrijvingen - Overige materiële vaste activa"),
    ("Afschrijvingen", "Afschrijvingen - Overige materiële vaste activa"),
    ("Algemene / overige kosten", "Overige bedrijfskosten - Andere kosten"),
    ("Auto's", "Materiële vaste activa - Overige materiële vaste activa"),
    ("Bank", "Liquide middelen - Liquide middelen"),
    ("Bankkosten", "Overige bedrijfskosten - Andere kosten"),
    ("Betaalde / ontvangen btw", "Btw - Btw betaald/ontvangen"),
    ("Betaalde / ontvangen btw over voorgaand jaar", "Btw - Btw betaald/ontvangen"),
    ("Betalings- en afrondingsverschillen", "Overige bedrijfskosten - Andere kosten"),
    ("Boetes", "Overige bedrijfskosten - Andere kosten"),
    ("Borg", "Vorderingen - Overige vorderingen"),
    ("Brandstofkosten auto", "Overige bedrijfskosten - Auto- en transportkosten"),
    ("Crediteuren", "Kortlopende schulden - Crediteuren"),
    ("Debiteuren", "Vorderingen - Debiteuren"),
    ("Deels aftrekbare kosten", "Overige bedrijfskosten - Andere kosten"),
    ("Eten en drinken in de horeca", "Overige bedrijfskosten - Andere kosten"),
    ("Eten en drinken op kantoor", "Overige bedrijfskosten - Andere kosten"),
    ("Huisvestingskosten", "Overige bedrijfskosten - Huisvestingskosten"),
    ("Inkoopkosten materiaal", "Inkoopkosten en uitbesteed werk - Inkoopprijs van de verkopen"),
    ("Investeringen", "Materiële vaste activa - Overige materiële vaste activa"),
    ("Kas", "Liquide middelen - Liquide middelen"),
    ("Kosten onderhoud auto", "Overige bedrijfskosten - Auto- en transportkosten"),
    ("Kosten overig auto", "Overige bedrijfskosten - Auto- en transportkosten"),
    ("Kruisposten / Spaartransactie", "Liquide middelen - Kruisposten"),
    ("Leningen", "Langlopende schulden - Overige langlopende schulden"),
    ("Omzet", "Opbrengsten - Omzet"),
    ("Opleidingen / trainingen", "Overige bedrijfskosten - Andere kosten"),
    ("Oudedagsreserve", "Ondernemingsvermogen - Oudedagsreserve"),
    ("Overboekingsrekening winst", "Systeemrekening winst en verlies - Overboekingsrekening winst"),
    ("Privé-stortingen en -opnames", "Ondernemingsvermogen - Gestort en opgevraagd kapitaal"),
    ("Promotie- en advertentiekosten", "Overige bedrijfskosten - Verkoopkosten"),
    ("Reiskosten", "Overige bedrijfskosten - Auto- en transportkosten"),
    ("Rente betaald", "Financiële baten en lasten - Rentelasten en soortgelijke kosten"),
    ("Rente ontvangen", "Financiële baten en lasten - Opbrengsten van banktegoeden"),
    ("Representatiekosten / Relatiegeschenken", "Overige bedrijfskosten - Andere kosten"),
    ("Softwarekosten", "Overige bedrijfskosten - Andere kosten"),
    ("Te betalen btw", "Btw - Btw te betalen/ontvangen"),
    ("Te vorderen btw", "Btw - Btw te betalen/ontvangen"),
    ("Telefoonkosten / internet", "Overige bedrijfskosten - Andere kosten"),
    ("Verzekeringen", "Overige bedrijfskosten - Andere kosten"),
    ("Voorraad", "Voorraad - Voorraad"),
    ("Vraagposten", "Kortlopende schulden - Nog te controleren posten"),
    ("Winstreserves", "Ondernemingsvermogen - Winstreserve"),
    ("Zakelijke Spaarrekening", "Liquide middelen - Liquide middelen"),
]

BTW_TARIEVEN = [
    ("21%", 21, "1a"),
    ("9%", 9, "1b"),
    ("Verlegd binnen NL", 0, "1e"),
    ("21% voorbelasting", 21, "5b"),
    ("9% voorbelasting", 9, "5b"),
]


def seed(db: Session) -> None:
    if db.query(Categorie).count() == 0:
        for naam, type_ in CATEGORIEEN:
            db.add(Categorie(naam=naam, type=type_))
    if db.query(BtwTarief).count() == 0:
        for omschrijving, pct, rubriek in BTW_TARIEVEN:
            db.add(BtwTarief(omschrijving=omschrijving, percentage=pct, rubriek=rubriek))
    if db.query(Instellingen).count() == 0:
        db.add(Instellingen(factuur_jaar=date.today().year, factuur_volgnummer=1))
    zorg_voor_periodes(db, date.today().year)
    db.commit()


def zorg_voor_periodes(db: Session, jaar: int) -> None:
    if db.query(Periode).filter(Periode.jaar == jaar).count() == 0:
        for nummer in range(0, 14):
            db.add(Periode(jaar=jaar, nummer=nummer, open=True))
