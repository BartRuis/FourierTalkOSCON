# Boekhoudapp

Eigen boekhoudapplicatie voor zzp (eenmanszaak), naar het model van Knab Boekhouden / DigiBoox.
Zie `../PLAN_VAN_AANPAK.md` voor het volledige plan; dit is **fase 1–2: het fundament + facturatie**.

## Wat zit erin (huidige stand)

- **Double-entry kern**: elke actie boekt een journaalpost in een dagboek (verkoopboek, inkopen,
  bank, memoriaal); posten die niet in balans zijn worden geweigerd. Rekeningschema (45
  categorieën), btw-tarieven en periodes 0–13 worden bij de eerste start geseed.
- **Relaties**: klanten beheren (bedrijf/particulier, factuuradres, archiveren).
- **Producten**: snelkeuze-regels voor de factuureditor.
- **Facturen**: concept → definitief (opeenvolgend nummer `jaar-XXXX`, journalisering
  Debiteuren/Omzet/Te betalen btw) → betaald (Bank/Debiteuren). Regels met aantal × stukprijs,
  btw per regel, korting-percentage, **PDF-download** (WeasyPrint) — versturen doe je zelf per mail.
- **Mutaties**: het grootboek-venster, per jaar.
- **Winst & verlies** en een dashboard met tegels.
- **Instellingen**: bedrijfsgegevens (op de factuur-PDF), betaaltermijn, volgnummer.

Nog niet (volgende fases): offertes, uren/projecten/ritten, kosten & bonnen, afschrijvingen,
bankimport (CSV/CAMT), btw-aangiftescherm, balans, creditfacturen, logo op de PDF.

## Lokaal draaien

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open http://localhost:8000 — vul eerst je bedrijfsgegevens in onder *Instellingen*.
WeasyPrint heeft systeembibliotheken nodig (op Debian/Ubuntu: `libpango-1.0-0 libpangoft2-1.0-0`);
in Docker zit dat er al in.

## Op de NAS (Docker)

```bash
docker compose up -d --build
```

De database en (straks) bonnen staan in `./data` — **neem die map op in je NAS-back-up**
(bewaarplicht: 7 jaar). De app heeft geen authenticatie; draai hem alleen op je eigen
netwerk of zet er een reverse proxy met login voor.

## Tests

```bash
pytest
```

De tests dekken de boekhoudkern: balansvalidatie, gesloten periodes, factuurtotalen
(gecontroleerd tegen een echt Knab-voorbeeld: € 58.700 subtotaal, 10% korting,
€ 11.094,30 btw), opeenvolgende nummering met jaarroulatie en de journalisering van
definitief maken en betalen.
