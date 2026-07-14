from decimal import Decimal

from fastapi import APIRouter, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BtwTarief, Product
from ..templating import render

router = APIRouter(prefix="/producten")


def _btw_tarieven(db: Session):
    return db.query(BtwTarief).filter(BtwTarief.gearchiveerd == False).all()  # noqa: E712


@router.get("", response_class=HTMLResponse)
def lijst(db: Session = Depends(get_db)):
    producten = (
        db.query(Product).filter(Product.gearchiveerd == False).order_by(Product.naam).all()  # noqa: E712
    )
    return render("producten/lijst.html", producten=producten, actief="producten")


@router.get("/nieuw", response_class=HTMLResponse)
def nieuw(db: Session = Depends(get_db)):
    return render("producten/form.html", product=None, btw_tarieven=_btw_tarieven(db), actief="producten")


@router.get("/{product_id}", response_class=HTMLResponse)
def bewerken(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    return render("producten/form.html", product=product, btw_tarieven=_btw_tarieven(db), actief="producten")


@router.post("/opslaan")
def opslaan(
    db: Session = Depends(get_db),
    product_id: int | None = Form(None),
    naam: str = Form(...),
    opmerking: str = Form(""),
    bedrag: str = Form("0"),
    btw_tarief_id: int = Form(...),
):
    product = db.get(Product, product_id) if product_id else Product()
    product.naam = naam
    product.opmerking = opmerking
    product.bedrag_cents = int(Decimal(bedrag.replace(",", ".")) * 100)
    product.btw_tarief_id = btw_tarief_id
    db.add(product)
    db.commit()
    return RedirectResponse("/producten", status_code=303)


@router.post("/{product_id}/archiveer")
def archiveer(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    product.gearchiveerd = True
    db.commit()
    return RedirectResponse("/producten", status_code=303)
