from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Instellingen(Base):
    """Eén rij met de bedrijfs- en app-instellingen."""

    __tablename__ = "instellingen"

    id: Mapped[int] = mapped_column(primary_key=True)
    bedrijfsnaam: Mapped[str] = mapped_column(String, default="")
    adres: Mapped[str] = mapped_column(String, default="")
    postcode: Mapped[str] = mapped_column(String, default="")
    stad: Mapped[str] = mapped_column(String, default="")
    land: Mapped[str] = mapped_column(String, default="Nederland")
    email: Mapped[str] = mapped_column(String, default="")
    telefoon: Mapped[str] = mapped_column(String, default="")
    iban: Mapped[str] = mapped_column(String, default="")
    kvk_nummer: Mapped[str] = mapped_column(String, default="")
    btw_id: Mapped[str] = mapped_column(String, default="")
    betaaltermijn_dagen: Mapped[int] = mapped_column(Integer, default=30)
    # Factuurnummering: formaat jaar-XXXX, volgnummer rouleert jaarlijks.
    factuur_jaar: Mapped[int] = mapped_column(Integer, default=0)
    factuur_volgnummer: Mapped[int] = mapped_column(Integer, default=1)


class BtwTarief(Base):
    __tablename__ = "btw_tarieven"

    id: Mapped[int] = mapped_column(primary_key=True)
    omschrijving: Mapped[str] = mapped_column(String)
    percentage: Mapped[float] = mapped_column(Numeric(5, 2))
    rubriek: Mapped[str] = mapped_column(String)  # 1a, 1b, 1e, 5b
    gearchiveerd: Mapped[bool] = mapped_column(Boolean, default=False)


class Categorie(Base):
    """Grootboekcategorie (rekeningschema)."""

    __tablename__ = "categorieen"

    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column(String, unique=True)
    type: Mapped[str] = mapped_column(String)  # bijv. "Opbrengsten - Omzet"
    gearchiveerd: Mapped[bool] = mapped_column(Boolean, default=False)


class Periode(Base):
    """Boekperiode: 0 = beginbalans, 1-12 = maanden, 13 = jaarafsluiting."""

    __tablename__ = "periodes"

    id: Mapped[int] = mapped_column(primary_key=True)
    jaar: Mapped[int] = mapped_column(Integer)
    nummer: Mapped[int] = mapped_column(Integer)
    open: Mapped[bool] = mapped_column(Boolean, default=True)


class Relatie(Base):
    __tablename__ = "relaties"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String, default="bedrijf")  # bedrijf | particulier
    naam: Mapped[str] = mapped_column(String)
    contactpersoon: Mapped[str] = mapped_column(String, default="")
    email: Mapped[str] = mapped_column(String, default="")
    telefoon: Mapped[str] = mapped_column(String, default="")
    adres: Mapped[str] = mapped_column(String, default="")
    postcode: Mapped[str] = mapped_column(String, default="")
    stad: Mapped[str] = mapped_column(String, default="")
    land: Mapped[str] = mapped_column(String, default="Nederland")
    factuuradres: Mapped[str] = mapped_column(Text, default="")  # vrij tekstblok op de factuur
    notities: Mapped[str] = mapped_column(Text, default="")
    gearchiveerd: Mapped[bool] = mapped_column(Boolean, default=False)

    facturen: Mapped[list["Factuur"]] = relationship(back_populates="relatie")


class Product(Base):
    """Snelkeuze-regel voor in de factuureditor."""

    __tablename__ = "producten"

    id: Mapped[int] = mapped_column(primary_key=True)
    naam: Mapped[str] = mapped_column(String)
    opmerking: Mapped[str] = mapped_column(String, default="")
    bedrag_cents: Mapped[int] = mapped_column(Integer, default=0)
    btw_tarief_id: Mapped[int | None] = mapped_column(ForeignKey("btw_tarieven.id"))
    gearchiveerd: Mapped[bool] = mapped_column(Boolean, default=False)

    btw_tarief: Mapped[BtwTarief | None] = relationship()


class Factuur(Base):
    __tablename__ = "facturen"

    id: Mapped[int] = mapped_column(primary_key=True)
    nummer: Mapped[str | None] = mapped_column(String, unique=True)  # toegekend bij definitief maken
    status: Mapped[str] = mapped_column(String, default="concept")  # concept | definitief | betaald
    factuurdatum: Mapped[date] = mapped_column(Date, default=date.today)
    relatie_id: Mapped[int | None] = mapped_column(ForeignKey("relaties.id"))
    korting_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=0)
    notities: Mapped[str] = mapped_column(Text, default="")
    aangemaakt_op: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)

    relatie: Mapped[Relatie | None] = relationship(back_populates="facturen")
    regels: Mapped[list["FactuurRegel"]] = relationship(
        back_populates="factuur", cascade="all, delete-orphan", order_by="FactuurRegel.volgorde"
    )


class FactuurRegel(Base):
    __tablename__ = "factuur_regels"

    id: Mapped[int] = mapped_column(primary_key=True)
    factuur_id: Mapped[int] = mapped_column(ForeignKey("facturen.id"))
    volgorde: Mapped[int] = mapped_column(Integer, default=0)
    omschrijving: Mapped[str] = mapped_column(String, default="")
    aantal: Mapped[float] = mapped_column(Numeric(12, 2), default=1)
    bedrag_cents: Mapped[int] = mapped_column(Integer, default=0)  # stukprijs excl. btw
    btw_tarief_id: Mapped[int | None] = mapped_column(ForeignKey("btw_tarieven.id"))

    factuur: Mapped[Factuur] = relationship(back_populates="regels")
    btw_tarief: Mapped[BtwTarief | None] = relationship()


class JournaalPost(Base):
    __tablename__ = "journaal_posten"

    id: Mapped[int] = mapped_column(primary_key=True)
    datum: Mapped[date] = mapped_column(Date)
    dagboek: Mapped[str] = mapped_column(String)  # verkoopboek | inkopen | bank | memoriaal
    jaar: Mapped[int] = mapped_column(Integer)
    periode_nummer: Mapped[int] = mapped_column(Integer)
    omschrijving: Mapped[str] = mapped_column(String, default="")
    factuur_id: Mapped[int | None] = mapped_column(ForeignKey("facturen.id"))

    regels: Mapped[list["JournaalRegel"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    factuur: Mapped[Factuur | None] = relationship()


class JournaalRegel(Base):
    __tablename__ = "journaal_regels"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("journaal_posten.id"))
    categorie_id: Mapped[int] = mapped_column(ForeignKey("categorieen.id"))
    debet_cents: Mapped[int] = mapped_column(Integer, default=0)
    credit_cents: Mapped[int] = mapped_column(Integer, default=0)
    relatie_id: Mapped[int | None] = mapped_column(ForeignKey("relaties.id"))

    post: Mapped[JournaalPost] = relationship(back_populates="regels")
    categorie: Mapped[Categorie] = relationship()
    relatie: Mapped[Relatie | None] = relationship()
