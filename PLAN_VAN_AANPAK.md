# Plan van aanpak — Eigen boekhoudapp (naar voorbeeld van Knab Boekhouden)

**Doel:** een zelfgebouwde boekhoudapplicatie voor eigen gebruik als zzp'er, met de functionaliteiten van Knab Boekhouden die jij daadwerkelijk gebruikt. Geen multi-tenant SaaS, geen team-features — één gebruiker, jouw administratie, volledige controle over je eigen data.

---

## 1. Uitgangspunten

- **Eén gebruiker** (jij), dus geen ingewikkeld rollen-/rechtensysteem.
- **Eigen data, eigen beheer:** alles draait lokaal of op een eigen (goedkope) server; data is altijd exporteerbaar.
- **Wettelijke eisen als leidraad, niet de Knab-UI:** we bouwen de *functies* na, niet pixel-voor-pixel het design. Wel gebruiken we jouw screenshots om workflows en schermen te modelleren.
- **Nederlandse zzp-context:** btw-aangifte per kwartaal, factuureisen Belastingdienst, 7 jaar bewaarplicht (10 jaar bij onroerend goed), kleineondernemersregeling (KOR) optioneel.

## 2. Fase 0 — Inventarisatie & prioritering (samen met jou)

Dit is de eerste concrete stap en hier heb ik jouw input voor nodig:

1. **Screenshots delen** van elk scherm in Knab Boekhouden dat je gebruikt: dashboard, facturen, offertes, bonnetjes, btw-aangifte, transacties/koppelen, rapportages, instellingen (factuurnummering, btw-tarieven, huisstijl).
2. **Feature-lijst opstellen** op basis van de screenshots, en per feature aangeven:
   - **Must have** — gebruik je elke week/maand;
   - **Should have** — gebruik je per kwartaal (bijv. btw-aangifte);
   - **Could have** — handig maar niet essentieel;
   - **Won't have** — gebruik je nooit (schrappen we).
3. **Data-export uit Knab** veiligstellen: facturen (PDF/UBL), transacties (CSV/CAMT.053), klantgegevens, bonnetjes. Dit dient twee doelen: migratie van je historie én voorbeelddata om mee te ontwikkelen.
4. **Beslissingen vastleggen** (zie §7, openstaande keuzes).

**Resultaat:** definitieve featurelijst + gemigreerde voorbeelddata.

## 3. Verwachte functionele scope

Op basis van wat Knab Boekhouden biedt voor zzp'ers; we strepen weg/vullen aan na fase 0:

| Domein | Functionaliteit |
|---|---|
| **Facturatie** | Facturen maken/versturen (PDF + e-mail), factuurnummering, btw-tarieven (21/9/0/verlegd/vrijgesteld), herinneringen, creditfacturen, eigen huisstijl/logo, UBL-export |
| **Offertes** | Offerte maken, versturen, omzetten naar factuur |
| **Klanten** | Klantenbestand met adres-, btw- en KVK-gegevens |
| **Uitgaven & bonnetjes** | Bonnetje/factuur uploaden (foto/PDF), koppelen aan transactie, btw eruit registreren |
| **Banktransacties** | Import (CSV/CAMT.053, evt. later automatische bankkoppeling), categoriseren, koppelen aan facturen/bonnetjes, afletteren |
| **Btw** | Kwartaaloverzicht per rubriek (1a t/m 5b) klaar om over te typen in Mijn Belastingdienst Zakelijk, ICP-opgaaf indien nodig |
| **Rapportages** | Winst & verlies, omzet per klant, openstaande facturen, reservering inkomstenbelasting, jaaroverzicht voor de aangifte IB |
| **Overig** | Zoeken, export (CSV/PDF), back-ups |

## 4. Voorgestelde architectuur

**Aanbeveling: lokaal draaiende webapp met SQLite.** Simpel, geen hostingkosten, data blijft bij jou, en een browser-UI is het meest geschikt om Knab-achtige schermen na te bouwen.

- **Backend:** Python (FastAPI) of Node/TypeScript — keuze afhankelijk van waar jij je comfortabel bij voelt (zie §7).
- **Database:** SQLite (één bestand = triviale back-ups; ruim voldoende voor één administratie).
- **Frontend:** server-rendered met lichte interactiviteit (bijv. HTMX/Alpine) óf React/Next.js als je een rijkere UI wilt.
- **PDF-generatie:** HTML-template → PDF (bijv. WeasyPrint of Playwright) voor facturen en offertes.
- **Bestanden:** bonnetjes/PDF's op schijf naast de database, met hash-verwijzing in de database.
- **Back-up:** automatische versleutelde back-up van database + bestanden naar cloud-opslag (bewaarplicht!).

**Kern-datamodel (eerste opzet):**

```
Klant ──< Offerte ──> Factuur ──< Factuurregel (btw-tarief per regel)
                        │
Transactie >──koppeling──┤
     │                   └──< Betaling
     └── Categorie (grootboek-achtig, incl. btw-behandeling)
Bonnetje/Inkoopfactuur ──> Transactie-koppeling + btw-bedrag
BtwPeriode (kwartaal) ── berekend uit facturen + uitgaven (of uit betalingen, bij kasstelsel)
```

Belangrijk ontwerpprincipe: **facturen zijn onveranderlijk na versturen** (correcties via creditfactuur) en **factuurnummers zijn opeenvolgend** — eisen van de Belastingdienst.

## 5. Fasering van de bouw

Elke fase levert iets op dat je direct kunt gebruiken.

**Fase 1 — Fundament (week 1–2)**
Projectopzet, datamodel, migraties, klantenbeheer, instellingen (bedrijfsgegevens, btw-id, factuurnummering, logo). Import van je Knab-klantenbestand.

**Fase 2 — Facturatie (week 2–4)**
Factuur maken/bewerken (concept) → definitief maken → PDF genereren → per e-mail versturen. Creditfacturen, openstaande-facturenlijst, betaalstatus. *Vanaf hier kun je al factureren vanuit je eigen app.*

**Fase 3 — Bank & uitgaven (week 4–6)**
CSV/CAMT-import van transacties, categoriseren (met onthouden-regels: "afzender X → categorie Y"), bonnetjes uploaden en koppelen, facturen afletteren tegen ontvangsten.

**Fase 4 — Btw & rapportages (week 6–8)**
Btw-kwartaaloverzicht per rubriek met onderbouwing (klikbaar naar de onderliggende facturen/bonnetjes), winst & verlies, IB-reservering, jaaroverzicht. *Doel: je eerstvolgende btw-aangifte doe je op basis van je eigen app, met Knab ernaast ter controle.*

**Fase 5 — Migratie & parallel draaien (1 kwartaal)**
Historie uit Knab importeren, één volledig kwartaal beide systemen naast elkaar draaien en de btw-cijfers vergelijken. Pas na een kloppend kwartaal zeg je Knab Boekhouden op.

**Fase 6 — Nice-to-haves (optioneel, daarna)**
Offertes, automatische bankkoppeling (PSD2 via bijv. GoCardless/Enable Banking), OCR op bonnetjes, urenregistratie, kilometerregistratie, betaallinks op facturen.

## 6. Risico's & aandachtspunten

- **Correctheid boven features:** een btw-fout kost geld en gedoe. Daarom: geautomatiseerde tests op alle btw-berekeningen, en fase 5 (parallel draaien) niet overslaan.
- **Bewaarplicht:** back-upstrategie is geen bijzaak; 7 jaar data moet veilig staan. Test ook het *terugzetten* van een back-up.
- **Bankkoppeling:** automatische PSD2-koppelingen kosten geld of hebben beperkingen voor particulier gebruik; CSV-import is gratis en betrouwbaar — daarom pas in fase 6.
- **Scope creep:** de MoSCoW-lijst uit fase 0 is heilig; nieuwe ideeën gaan op de "later"-lijst.
- **E-mailbezorging:** facturen mailen vereist een nette afzender (eigen domein + bijv. Postmark/SES of je eigen SMTP), anders belanden facturen in spam.

## 7. Openstaande keuzes (graag jouw antwoord)

1. **Techniek:** heb je een voorkeur voor Python of TypeScript (of iets anders)? Wil je zelf aan de code kunnen sleutelen?
2. **Draaiomgeving:** lokaal op je eigen computer, thuisserver/NAS, of een kleine VPS zodat je er ook mobiel bij kunt?
3. **Stelsel:** factuurstelsel (btw op factuurdatum, gebruikelijk) of kasstelsel?
4. **KOR:** doe je mee aan de kleineondernemersregeling?
5. **Bankkoppeling:** is handmatige CSV-import (bijv. wekelijks) acceptabel als start?
6. **Welke Knab-functies gebruik je echt?** — te beantwoorden met de screenshots uit fase 0.

## 8. Eerstvolgende concrete stappen

1. Jij deelt screenshots van de Knab-schermen die je gebruikt + antwoorden op §7.
2. Ik werk de featurelijst en het datamodel definitief uit op basis daarvan.
3. Repository voor de app opzetten en starten met fase 1.
