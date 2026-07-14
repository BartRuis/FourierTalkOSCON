# Plan van aanpak — Eigen boekhoudapp (nabouw Knab Boekhouden / DigiBoox)

**Doel:** een zelfgebouwde boekhoudapplicatie voor eigen gebruik als zzp'er (eenmanszaak), met de functionaliteiten van Knab Boekhouden die jij daadwerkelijk gebruikt. Eén gebruiker, eigen data, volledige controle.

**Status:** fase 0 (inventarisatie) is afgerond op basis van ~70 screenshots van de complete app, een voorbeeld-offerte-PDF en drie DigiBoox-exports (ritten, uren, categorieën). Dit document is de definitieve featurelijst + bouwplan. Knab Boekhouden blijkt een white-label van **DigiBoox**.

---

## 1. Kerninzicht uit de inventarisatie: het is dubbel boekhouden

De schermen "Kolommenbalans", "Mutaties" en "Balans" laten zien dat elke handeling (factuur opslaan, bon inboeken, banktransactie koppelen, afschrijving, rittenregistratie) onder water een **journaalpost in een dagboek** produceert: *Verkoopboek*, *Inkopen*, *Bank* of *Memoriaal*. Voorbeeld uit de mutaties: één factuur van € 63.924,30 wordt geboekt als Debiteuren (debet) tegen Omzet € 52.830 + Te betalen btw € 11.094 (credit).

**Architectuurbeslissing:** we bouwen een kleine double-entry kern (journaalposten met debet/credit op categorieën). Alle rapportages (balans, W&V, kolommenbalans, mutaties, btw-aangifte) zijn dan *afleidingen* van één grootboek in plaats van los geprogrammeerde optellingen. Dit is de enige manier om gegarandeerd kloppende cijfers te krijgen en is precies hoe het origineel werkt.

De categorieën-export levert het complete rekeningschema: 45 categorieën met hun type (bijlage A). Dit nemen we 1-op-1 over als startschema.

## 2. Functionele scope per module (zoals aangetroffen)

Prioritering als voorstel; pas aan waar nodig. ✅ = must, 🔶 = should, ⚪ = could, ❌ = won't.

### 2.1 Relaties ✅
Bedrijf/particulier, bedrijfsnaam (origineel zoekt in KvK-register), contactpersoon, e-mail, telefoon, adres, apart factuuradres (vrije tekst), notities, archiveren. *KvK-zoeken kan later via de gratis KVK API (⚪).*

### 2.2 Offertes ✅
Offertedatum, klant, referentie, vervaldatum (default +1 maand), begeleidende tekst, interne notities, regels (omschrijving/aantal/bedrag excl.-incl. schakelaar/btw-%), kortingsregel (%), productkoppeling per regel, nummering `yyyy-XXXX`, statussen (Nieuw/Niet verstuurd → verstuurd → geaccepteerd), PDF-generatie, versturen per e-mail (met onderwerp/tekst-template, bijlagen, voorbeeld), **"Offerte bekijken en accepteren"-link in de mail** (🔶 — vereist een publiek bereikbaar endpointje), **Factuur maken** vanuit offerte, kopiëren, bestand uploaden bij offerte.

### 2.3 Facturen ✅
Zelfde regelseditor als offertes + factuurdatum, betaaltermijn uit instellingen (30 dgn), status open/x-dagen-open/betaald, **urenkoppeling**: geselecteerde uren als factuurregels + optionele urenspecificatie-bijlage, PDF, verstuur factuur / verstuur herinnering / zet op 'Verstuurd', **maak creditfactuur**, zet op betaald (of automatisch via bankkoppeling), kopiëren, upload bijlage. Tab **Periodieke facturen** ⚪ (alleen bouwen als je die echt gebruikt). Factuurnummer strikt opeenvolgend, roulatie jaarlijks, formaat instelbaar (`yyyy-XXXX`); factuur onveranderlijk na versturen (correctie via creditfactuur).

### 2.4 Kosten (inkoop & bonnen) ✅
Datum, leverancier (relatie), factuurnummer leverancier, regels (omschrijving/bedrag/btw-%/**categorie**), bon/factuur-upload met preview naast het formulier ("Bon-weergave" vs "Inkoop-weergave"), status open/betaald, creditfactuur, zet op betaald. **Afschrijven vanaf inkoopregel**: investering → afschrijving met startdatum, aanschafwaarde, aantal maanden (bijv. 60), restwaarde, categorie balans (Investeringen) + categorie kosten (Afschrijvingen); maandelijkse memoriaalboekingen, statusoverzicht (afgeschreven bedrag, huidige waarde, laatste afschrijving), afschrijvingenlijst, stoppen. ScanPilot AI (OCR + mail-inbox voor bonnen) ❌ voor de start — handmatig invoeren met bon-preview is prima; eventueel later lokaal OCR ⚪.

### 2.5 Bank/kas ✅
Meerdere rekeningen (Bank, Kas, Zakelijke spaarrekening; toevoegen mogelijk), **te-verwerken-wachtrij** met teller, transactielijst met koppelstatus, export. Per geïmporteerde transactie een verwerkscherm met tabs **Factuur / Inkoop / Spaar / Privé / Overig**, automatische koppelsuggestie ("Deze transactie is automatisch door het systeem gekoppeld — controleer en klik op Opslaan"), deelbetalingen via meerdere regels, "Opslaan en volgende" / "Overslaan" voor snel doorwerken. Opties: **Bankimport** (CSV/CAMT ✅), **Bankkoppeling via Ponto** (❌ start, ⚪ later), **Automatische verwerkregels** (🔶 — "afzender X → categorie Y"), handmatige transactie ✅.

### 2.6 Btw ✅ (het kwartaalritueel)
Overzicht per jaar: 4 kwartalen met status (niet verstuurd / nog niet afgelopen / verstuurd) en bedrag. Aangiftescherm met **rubrieken 1a–5b** (compact: alleen relevante regels; uitklapbaar naar alle regels), omzet + omzetbelasting per rubriek, **klikbare onderbouwing per regel**, "Btw te betalen"-totaal. Versturen naar Belastingdienst via Digipoort ❌ — wij maken een **overtyp-overzicht voor Mijn Belastingdienst Zakelijk** + "markeer als verstuurd". Opgaaf ICP: alleen een melding zolang niet van toepassing ⚪. Btw-percentages instelbaar en gemapt op rubriek (21%→1a, 9%→1b, verlegd→1e, voorbelasting→5b).

### 2.7 Uren & Projecten ✅
Projecten: type **Factureerbaar** (klant + uurtarief) of **Intern**, notities, archiveren. Uren: invoer (datum, tijdsduur, project, omschrijving, opslaan+nieuw), weekoverzicht (ma–zo grid per week, filter), zoeken/lijst met totaal, export. **Uren factureren**: selecteer niet-gefactureerde uren per project → factuur met tarief × uren, urenspecificatie aan/uit, uren krijgen factuurkoppeling.

### 2.8 Ritten 🔶
Ritregistratie: datum, vertrekpunt/bestemming (vrij adres of adres van relatie), vervoermiddel (Auto/Motor/Fiets; zakelijk of privé; "auto van de zaak?"), afstand met **Bereken-knop** (routeberekening — bij ons: OpenStreetMap/OSRM ⚪ of handmatig invullen), zakelijk-vinkje met vergoeding **€ 0,25/km** (instelbaar per jaar), kilometerstanden begin/eind, omschrijving, opslaan+retourrit. Lijst met totalen zakelijk/privé, export. Genereert memoriaalboeking Reiskosten tegen Privé-stortingen.

### 2.9 Overzichten ✅
- **Winst- en verliesrekening**: opbrengsten/kosten gegroepeerd, periode-selectie, export.
- **Balans**: activa/passiva per categoriegroep, per einde periode.
- **Kolommenbalans** 🔶: beginbalans / mutaties / eindbalans in debet-credit-kolommen.
- **Kosten en omzet**: staafgrafiek per maand + tabel, groepering instelbaar.
- **Mutaties** ✅: alle journaalregels, filter op periode/type(dagboek)/categorie, zoeken, export — het audit-venster op het grootboek.
- Historisch overzicht debiteuren/crediteuren ⚪.

### 2.10 Overige boekingen (memoriaal) 🔶
Vrije memoriaalboeking + zoeken. Wizards: **Beginbalans** ✅ (nodig voor migratie!), **Jaarafsluiting** ✅ (winst → winstreserves), Bijtelling ⚪, Financial lease ❌, Btw privé-gebruik auto ⚪, Extra btw-teruggave ⚪.

### 2.11 Inkomstenbelasting ⚪
In het origineel een betaalde wizard (€ 130) die aangifte indient. Voor ons: **jaarrapport voor de IB-aangifte** (fiscale winstberekening, balans, W&V, investeringen/afschrijvingen, gereden km's, urenoverzicht voor het urencriterium) dat je naast de aangifte op Mijn Belastingdienst legt. Geen indiening.

### 2.12 Instellingen ✅
Bedrijfsgegevens (naam, e-mail, telefoon, IBAN, KvK, OB-nummer, btw-id, betaaltermijn, rechtsvorm, branche, btw-aangifte per kwartaal), bedrijfslogo, lay-out factuur/offerte, factuur-/offertenummering (formaat + roulatie + huidig volgnummer), bcc-aan-jezelf bij e-mail, e-mailtekst-templates per type (Factuur, Creditfactuur, Herinnering, Aanmaning, Ingebrekestelling, Offerte) met placeholders zoals `{nummer}` en bijlagen, betaalmethodes, btw-percentages, **periodes 0–13 met open/gesloten status** (0 = beginbalans, 13 = jaarafsluiting), categorieënbeheer, producten (naam, opmerking, bedrag, btw, categorie — als snelkeuze in regeleditor), vervoermiddelen. Koppelingen (Mollie iDEAL-betaallinks, Ponto) ❌ start / ⚪ later. Gebruikersbeheer ❌ (single user). Dashboard ✅: tegels (te ontvangen omzet, te betalen kosten, winst, btw huidig kwartaal), omzet/kosten-grafiek, laatste facturen, bank/kas-saldi, winst, balans-samenvatting, debiteuren/crediteuren.

## 3. Architectuur

**Aanbeveling: lokaal draaiende webapp, SQLite, alles in één proces.**

- **Backend:** Python (FastAPI + SQLAlchemy) of TypeScript (Node/Fastify + Drizzle) — jouw keuze (§6).
- **Database:** SQLite; bonnen/PDF's als bestanden ernaast met hash-verwijzing.
- **Frontend:** server-rendered + HTMX/Alpine (snel te bouwen, Knab-achtige schermen zijn klassieke formulieren/lijsten) óf React als je een rijkere UI wilt.
- **PDF:** HTML-template → PDF (WeasyPrint of Playwright) voor factuur/offerte/urenspecificatie, naar het model van de voorbeeld-PDF (logo, adresblok, KvK/btw-id/IBAN, regels, korting, btw-samenvatting).
- **E-mail:** SMTP met eigen domein (of Postmark/SES), bcc naar jezelf, templates met placeholders.
- **Back-up:** dagelijkse versleutelde kopie van db + bestanden naar cloud-opslag; restore-test hoort bij fase 1.

### Datamodel (kern)

```
Categorie (rekeningschema, bijlage A; type bepaalt balans/W&V-groepering)
JournaalPost (datum, dagboek: verkoop|inkoop|bank|memoriaal, periode, omschrijving, bron-verwijzing)
  └── JournaalRegel (categorie, debet|credit, bedrag, relatie?)          ← som debet = som credit
Periode (jaar, nr 0-13, open|gesloten)
Relatie (bedrijf|particulier, adres, factuuradres, e-mail, ...)
Product | BtwTarief (percentage, rubriek 1a|1b|1e|5b) | Instellingen
Offerte ──> Factuur ──< FactuurRegel (aantal, bedrag, btw-tarief, product?, korting%)
Factuur ──> JournaalPost (verkoopboek)   InkoopFactuur ──> JournaalPost (inkoopboek)
InkoopFactuur ──< InkoopRegel + Bestanden (bon-scan)
Afschrijving (aanschafwaarde, maanden, restwaarde, cat. balans, cat. kosten) ──< maandelijkse memoriaalposten
BankRekening ──< BankTransactie (geïmporteerd; status te-verwerken|verwerkt) ──> koppeling (factuur|inkoop|spaar|privé|overig) ──> JournaalPost (bankboek)
VerwerkRegel (matchpatroon → koppeltype/categorie)
Project (factureerbaar: klant+uurtarief | intern) ──< Uur (datum, duur, omschrijving, factuur?)
Vervoermiddel ──< Rit (van, naar, km, zakelijk?, kmstanden) ──> memoriaal reiskosten
```

## 4. Fasering

Elke fase eindigt met iets bruikbaars; volgorde volgt jouw workflow (offerte → uren → factuur → bank → btw).

| Fase | Inhoud | Resultaat |
|---|---|---|
| **1. Fundament** (wk 1–2) | Projectopzet, double-entry kern + categorieën (bijlage A), periodes, instellingen, relaties, producten, btw-tarieven, dashboard-skelet, back-up | Grootboek werkt; mutaties-scherm toont testboekingen |
| **2. Offertes & facturen** (wk 2–4) | Regeleditor, nummering, PDF, e-mail versturen (+bcc, templates), statussen, creditfactuur, offerte→factuur, verkoopboek-journalisering | Je kunt offreren en factureren vanuit eigen app |
| **3. Uren, projecten & ritten** (wk 4–5) | Projecten, ureninvoer + weekoverzicht, uren factureren met specificatie, ritten + km-vergoeding | Uren-tot-factuur-flow compleet |
| **4. Kosten & bank** (wk 5–7) | Inkoop + bon-upload met preview, afschrijvingen, CSV/CAMT-import, verwerk-wachtrij met tabs+suggesties, verwerkregels, handmatige transacties | Administratie sluitend: elke euro gecategoriseerd |
| **5. Btw & overzichten** (wk 7–8) | Btw-kwartaalscherm (rubrieken + onderbouwing), W&V, balans, kolommenbalans, kosten/omzet-grafiek, beginbalans- en jaarafsluitingswizard | Btw-aangifte uit eigen app (overtypen bij Belastingdienst) |
| **6. Migratie & parallel draaien** (1 kwartaal) | Historie importeren (relaties, facturen, uren, ritten, categorieën via DigiBoox-exports), beginbalans zetten, één vol kwartaal naast Knab draaien, btw-cijfers vergelijken | Vertrouwen om Knab op te zeggen |
| **7. Later (optioneel)** | Offerte-accepteerlink, periodieke facturen, Ponto-bankkoppeling, Mollie-betaallinks, OCR bonnen, KVK-zoeken, routeberekening ritten, IB-jaarrapport | Comfort-features |

## 5. Risico's & aandachtspunten

- **Correctheid boven features**: geautomatiseerde tests op journalisering (debet=credit), btw-rubriektoewijzing en afschrijvingsreeksen. Fase 6 (parallel kwartaal) niet inkorten.
- **Wettelijk**: opeenvolgende factuurnummers, facturen onveranderlijk na versturen, 7 jaar bewaarplicht → back-ups + restore-test, factuureisen (KvK, btw-id, datum, nummer) in de PDF-template.
- **E-mailbezorging**: facturen versturen vanaf eigen domein met SPF/DKIM, anders spam.
- **Scope**: het origineel is groot; de ❌/⚪-markeringen bewaken dat we alleen bouwen wat jij gebruikt.
- **Gegevens in testdata**: screenshots bevatten echte bedrijfsgegevens (KvK, btw-id, IBAN) — die horen in de app-instellingen, niet in de repo/seed-data.

## 6. Nog te beslissen door jou

1. **Techniek**: Python of TypeScript? Wil je zelf aan de code sleutelen?
2. **Draaiomgeving**: lokaal, NAS/thuisserver, of kleine VPS (nodig als je de offerte-accepteerlink en mobiel gebruik wilt)?
3. **MoSCoW-check**: kloppen de ✅/🔶/⚪/❌-inschattingen in §2? Vooral: periodieke facturen, ICP, kolommenbalans, bijtelling-wizard.
4. **KOR**: doe je mee aan de kleineondernemersregeling? (Verandert de btw-module.)
5. **Stelsel**: factuurstelsel aangenomen (zo werkt het origineel); klopt dat?
6. **E-mail**: versturen vanaf `@ruisengineering.com` — welke mailprovider/SMTP gebruik je nu?

## 7. Volgende stappen

1. Jij beantwoordt §6 (kan kort, puntsgewijs).
2. Nieuwe, aparte repository voor de app aanmaken; projectskelet + fase 1 starten.
3. Voor fase 6 t.z.t. volledige exports uit Knab veiligstellen (facturen-PDF's, transacties, relaties — naast de drie reeds gedeelde exports).

---

## Bijlage A — Rekeningschema (uit DigiBoox-export, 45 categorieën)

| Categorie | Type |
|---|---|
| Afschrijving auto's | Afschrijvingen – Overige materiële vaste activa |
| Afschrijvingen | Afschrijvingen – Overige materiële vaste activa |
| Algemene / overige kosten | Overige bedrijfskosten – Andere kosten |
| Auto's | Materiële vaste activa – Overige materiële vaste activa |
| Bank | Liquide middelen – Liquide middelen |
| Bankkosten | Overige bedrijfskosten – Andere kosten |
| Betaalde / ontvangen btw | Btw – Btw betaald/ontvangen |
| Betaalde / ontvangen btw over voorgaand jaar | Btw – Btw betaald/ontvangen |
| Betalings- en afrondingsverschillen | Overige bedrijfskosten – Andere kosten |
| Boetes | Overige bedrijfskosten – Andere kosten |
| Borg | Vorderingen – Overige vorderingen |
| Brandstofkosten auto | Overige bedrijfskosten – Auto- en transportkosten |
| Crediteuren | Kortlopende schulden – Crediteuren |
| Debiteuren | Vorderingen – Debiteuren |
| Deels aftrekbare kosten | Overige bedrijfskosten – Andere kosten |
| Eten en drinken in de horeca | Overige bedrijfskosten – Andere kosten |
| Eten en drinken op kantoor | Overige bedrijfskosten – Andere kosten |
| Huisvestingskosten | Overige bedrijfskosten – Huisvestingskosten |
| Inkoopkosten materiaal | Inkoopkosten en uitbesteed werk – Inkoopprijs van de verkopen |
| Investeringen | Materiële vaste activa – Overige materiële vaste activa |
| Kas | Liquide middelen – Liquide middelen |
| Kosten onderhoud auto | Overige bedrijfskosten – Auto- en transportkosten |
| Kosten overig auto | Overige bedrijfskosten – Auto- en transportkosten |
| Kruisposten / Spaartransactie | Liquide middelen – Kruisposten |
| Leningen | Langlopende schulden – Overige langlopende schulden |
| Omzet | Opbrengsten – Omzet |
| Opleidingen / trainingen | Overige bedrijfskosten – Andere kosten |
| Oudedagsreserve | Ondernemingsvermogen – Oudedagsreserve |
| Overboekingsrekening winst | Systeemrekening winst en verlies |
| Privé-stortingen en -opnames | Ondernemingsvermogen – Gestort en opgevraagd kapitaal |
| Promotie- en advertentiekosten | Overige bedrijfskosten – Verkoopkosten |
| Reiskosten | Overige bedrijfskosten – Auto- en transportkosten |
| Rente betaald | Financiële baten en lasten – Rentelasten |
| Rente ontvangen | Financiële baten en lasten – Opbrengsten van banktegoeden |
| Representatiekosten / Relatiegeschenken | Overige bedrijfskosten – Andere kosten |
| Softwarekosten | Overige bedrijfskosten – Andere kosten |
| Te betalen btw | Btw – Btw te betalen/ontvangen |
| Te vorderen btw | Btw – Btw te betalen/ontvangen |
| Telefoonkosten / internet | Overige bedrijfskosten – Andere kosten |
| Verzekeringen | Overige bedrijfskosten – Andere kosten |
| Voorraad | Voorraad – Voorraad |
| Vraagposten | Kortlopende schulden – Nog te controleren posten |
| Winstreserves | Ondernemingsvermogen – Winstreserve |
| Zakelijke Spaarrekening | Liquide middelen – Liquide middelen |

## Bijlage B — Btw-rubrieken in het aangiftescherm

Rubriek 1: prestaties binnenland (1a hoog, 1b laag, 1c overig, 1d privégebruik, 1e 0%/onbelast) · Rubriek 2: verleggingsregelingen binnenland (2a) · Rubriek 3: buitenland (3a uitvoer, 3b EU, 3c installatie/afstandsverkopen) · Rubriek 4: prestaties uit buitenland (4a buiten EU, 4b binnen EU) · Rubriek 5: voorbelasting (5b) → saldo "Btw te betalen/terug te vragen".
