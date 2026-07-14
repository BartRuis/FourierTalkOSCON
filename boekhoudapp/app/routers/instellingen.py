from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BtwTarief, Categorie, Instellingen
from ..templating import render

router = APIRouter(prefix="/instellingen")


@router.get("", response_class=HTMLResponse)
def tonen(db: Session = Depends(get_db)):
    return render(
        "instellingen.html",
        instellingen=db.query(Instellingen).one(),
        categorieen=db.query(Categorie).order_by(Categorie.naam).all(),
        btw_tarieven=db.query(BtwTarief).all(),
        actief="instellingen",
    )


@router.post("/opslaan")
def opslaan(
    db: Session = Depends(get_db),
    bedrijfsnaam: str = Form(""),
    adres: str = Form(""),
    postcode: str = Form(""),
    stad: str = Form(""),
    land: str = Form("Nederland"),
    email: str = Form(""),
    telefoon: str = Form(""),
    iban: str = Form(""),
    kvk_nummer: str = Form(""),
    btw_id: str = Form(""),
    betaaltermijn_dagen: int = Form(30),
    factuur_volgnummer: int = Form(1),
):
    instellingen = db.query(Instellingen).one()
    instellingen.bedrijfsnaam = bedrijfsnaam
    instellingen.adres = adres
    instellingen.postcode = postcode
    instellingen.stad = stad
    instellingen.land = land
    instellingen.email = email
    instellingen.telefoon = telefoon
    instellingen.iban = iban
    instellingen.kvk_nummer = kvk_nummer
    instellingen.btw_id = btw_id
    instellingen.betaaltermijn_dagen = betaaltermijn_dagen
    instellingen.factuur_volgnummer = factuur_volgnummer
    db.commit()
    return RedirectResponse("/instellingen", status_code=303)
