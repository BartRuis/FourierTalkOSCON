from datetime import date, datetime
from decimal import Decimal

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..facturen_service import bereken_totalen, maak_definitief, registreer_betaling
from ..ledger import BoekingsFout
from ..models import BtwTarief, Factuur, FactuurRegel, Instellingen, Product, Relatie
from ..pdf import factuur_pdf
from ..templating import render

router = APIRouter(prefix="/facturen")


def _context(db: Session):
    return {
        "relaties": db.query(Relatie).filter(Relatie.gearchiveerd == False).order_by(Relatie.naam).all(),  # noqa: E712
        "btw_tarieven": db.query(BtwTarief)
        .filter(BtwTarief.gearchiveerd == False, BtwTarief.rubriek.in_(["1a", "1b", "1e"]))  # noqa: E712
        .all(),
        "producten": db.query(Product).filter(Product.gearchiveerd == False).all(),  # noqa: E712
    }


@router.get("", response_class=HTMLResponse)
def lijst(db: Session = Depends(get_db)):
    facturen = db.query(Factuur).order_by(Factuur.factuurdatum.desc(), Factuur.id.desc()).all()
    rijen = [(f, bereken_totalen(f)) for f in facturen]
    totaal_excl = sum(t.totaal_excl for _, t in rijen)
    totaal_incl = sum(t.totaal_incl for _, t in rijen)
    return render(
        "facturen/lijst.html",
        rijen=rijen, totaal_excl=totaal_excl, totaal_incl=totaal_incl, vandaag=date.today(), actief="facturen",
    )


@router.get("/nieuw")
def nieuw(db: Session = Depends(get_db)):
    factuur = Factuur(factuurdatum=date.today())
    db.add(factuur)
    db.commit()
    return RedirectResponse(f"/facturen/{factuur.id}", status_code=303)


@router.get("/{factuur_id}", response_class=HTMLResponse)
def bewerken(factuur_id: int, foutmelding: str = "", db: Session = Depends(get_db)):
    factuur = db.get(Factuur, factuur_id)
    return render(
        "facturen/form.html",
        factuur=factuur, totalen=bereken_totalen(factuur), foutmelding=foutmelding,
        vandaag=date.today(), actief="facturen", **_context(db),
    )


@router.post("/{factuur_id}/opslaan")
def opslaan(
    factuur_id: int,
    db: Session = Depends(get_db),
    factuurdatum: str = Form(...),
    relatie_id: str = Form(""),
    korting_pct: str = Form("0"),
    notities: str = Form(""),
    regel_omschrijving: list[str] = Form([]),
    regel_aantal: list[str] = Form([]),
    regel_bedrag: list[str] = Form([]),
    regel_btw_tarief_id: list[str] = Form([]),
):
    factuur = db.get(Factuur, factuur_id)
    if factuur.status != "concept":
        return RedirectResponse(f"/facturen/{factuur_id}", status_code=303)

    factuur.factuurdatum = datetime.strptime(factuurdatum, "%Y-%m-%d").date()
    factuur.relatie_id = int(relatie_id) if relatie_id else None
    factuur.korting_pct = Decimal(korting_pct.replace(",", ".") or "0")
    factuur.notities = notities

    factuur.regels.clear()
    for volgorde, (omschrijving, aantal, bedrag, btw_id) in enumerate(
        zip(regel_omschrijving, regel_aantal, regel_bedrag, regel_btw_tarief_id)
    ):
        if not omschrijving.strip() and not bedrag.strip():
            continue
        factuur.regels.append(
            FactuurRegel(
                volgorde=volgorde,
                omschrijving=omschrijving.strip(),
                aantal=Decimal(aantal.replace(",", ".") or "1"),
                bedrag_cents=int(Decimal(bedrag.replace(",", ".") or "0") * 100),
                btw_tarief_id=int(btw_id),
            )
        )
    db.commit()
    return RedirectResponse(f"/facturen/{factuur_id}", status_code=303)


@router.post("/{factuur_id}/definitief")
def definitief(factuur_id: int, db: Session = Depends(get_db)):
    factuur = db.get(Factuur, factuur_id)
    try:
        maak_definitief(db, factuur)
        db.commit()
    except BoekingsFout as fout:
        db.rollback()
        return RedirectResponse(f"/facturen/{factuur_id}?foutmelding={fout}", status_code=303)
    return RedirectResponse(f"/facturen/{factuur_id}", status_code=303)


@router.post("/{factuur_id}/betaald")
def betaald(factuur_id: int, betaaldatum: str = Form(...), db: Session = Depends(get_db)):
    factuur = db.get(Factuur, factuur_id)
    try:
        registreer_betaling(db, factuur, datetime.strptime(betaaldatum, "%Y-%m-%d").date())
        db.commit()
    except BoekingsFout as fout:
        db.rollback()
        return RedirectResponse(f"/facturen/{factuur_id}?foutmelding={fout}", status_code=303)
    return RedirectResponse(f"/facturen/{factuur_id}", status_code=303)


@router.post("/{factuur_id}/verwijderen")
def verwijderen(factuur_id: int, db: Session = Depends(get_db)):
    factuur = db.get(Factuur, factuur_id)
    if factuur.status == "concept":
        db.delete(factuur)
        db.commit()
    return RedirectResponse("/facturen", status_code=303)


@router.get("/{factuur_id}/pdf")
def pdf(factuur_id: int, db: Session = Depends(get_db)):
    factuur = db.get(Factuur, factuur_id)
    instellingen = db.query(Instellingen).one()
    inhoud = factuur_pdf(factuur, instellingen)
    bestandsnaam = f"Factuur {factuur.nummer or 'concept'}.pdf"
    return Response(
        content=inhoud,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{bestandsnaam}"'},
    )
