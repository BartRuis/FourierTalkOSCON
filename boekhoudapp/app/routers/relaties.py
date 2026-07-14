from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Relatie
from ..templating import render

router = APIRouter(prefix="/relaties")


@router.get("", response_class=HTMLResponse)
def lijst(db: Session = Depends(get_db)):
    relaties = (
        db.query(Relatie).filter(Relatie.gearchiveerd == False).order_by(Relatie.naam).all()  # noqa: E712
    )
    return render("relaties/lijst.html", relaties=relaties, actief="relaties")


@router.get("/nieuw", response_class=HTMLResponse)
def nieuw():
    return render("relaties/form.html", relatie=None, actief="relaties")


@router.get("/{relatie_id}", response_class=HTMLResponse)
def bewerken(relatie_id: int, db: Session = Depends(get_db)):
    relatie = db.get(Relatie, relatie_id)
    return render("relaties/form.html", relatie=relatie, actief="relaties")


@router.post("/opslaan")
def opslaan(
    db: Session = Depends(get_db),
    relatie_id: int | None = Form(None),
    type: str = Form("bedrijf"),
    naam: str = Form(...),
    contactpersoon: str = Form(""),
    email: str = Form(""),
    telefoon: str = Form(""),
    adres: str = Form(""),
    postcode: str = Form(""),
    stad: str = Form(""),
    land: str = Form("Nederland"),
    factuuradres: str = Form(""),
    notities: str = Form(""),
):
    relatie = db.get(Relatie, relatie_id) if relatie_id else Relatie()
    relatie.type = type
    relatie.naam = naam
    relatie.contactpersoon = contactpersoon
    relatie.email = email
    relatie.telefoon = telefoon
    relatie.adres = adres
    relatie.postcode = postcode
    relatie.stad = stad
    relatie.land = land
    relatie.factuuradres = factuuradres
    relatie.notities = notities
    db.add(relatie)
    db.commit()
    return RedirectResponse("/relaties", status_code=303)


@router.post("/{relatie_id}/archiveer")
def archiveer(relatie_id: int, db: Session = Depends(get_db)):
    relatie = db.get(Relatie, relatie_id)
    relatie.gearchiveerd = True
    db.commit()
    return RedirectResponse("/relaties", status_code=303)
