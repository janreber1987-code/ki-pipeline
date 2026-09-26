# Energiefuchs-Engine: Übersicht für die Gegenprüfung

Stand dieses Dokuments: 2026-09-26. Die Quellen sind Notion (⚡ Energiefuchs, letzte Änderung 19.05.2026), Google Drive (Status-Snapshot 17./19.05.2026) und ein Repomix-Pack der gesamten Codebasis `energiefuchs-engine` (26.05.2026, 15'551 Zeilen, vollständig ausgewertet). Der Code liegt lokal unter Windows (`C:\Users\info\Desktop\jan privat\energiefuchs-engine\`). Dieses Repo (`ki-pipeline`) war leer. Seit dem 26.05. gibt es keine dokumentierten Änderungen mehr.

Markierungen: **[V]** = im Code oder in der Doku gesehen, **[P]** = plausibel, aber nicht belegt, **[A]** = Annahme oder Einschätzung des Autors.

---

## 1. Was Energiefuchs sein soll

Energiefuchs ist ein Remote-Voranalyse-Dienst für Hausbesitzer in der Schweiz, zuerst im Kanton BE, dann in SO. Er richtet sich an Hausbesitzer, die vor einem Heizungsersatz stehen. Aus GWR-Daten, öffentlichen Geodaten und einem Self-Service-Fragebogen mit 12–15 Fragen berechnet die Engine:

- Heizlast
- GEAK-Klassen (Vor-GEAK)
- WP-Eignung
- MuKEn- bzw. Standardlösungs-Check (SL7)
- Vollkosten über 20 Jahre (SIA 480)
- CO₂-Bilanz
- Fördercheck

Ergebnis ist ein Dossier in zwei Teilen: ein Kundenteil in Laiensprache und ein Experten-Annex. Einen Vor-Ort-Termin gibt es nicht.

**USP laut Doku [V]:** rechtssichere, verifizierte Grundlagen und Anti-Greenwashing. Der Dienst ist als Optionsdarstellungs-Tool gedacht, nicht als Empfehlungstool. Es gilt die harte Regel „Kantonsrecht nie von BE auf andere Kantone übertragen“.

**Positionierung, Stand 19.05. [V]:** Energiefuchs ist kein GEAK-Konkurrent, sondern **GEAK-Zulieferer**. Die Kette lautet: Hausbesitzer → Energiefuchs-Dossier → GEAK-Experte bestätigt → offizielles Zertifikat.

**Geschäftsmodell:** Es gibt drei verschiedene Stände, die sich widersprechen (siehe Abschnitt 5):

| Stand | Modell |
|---|---|
| 05.05. (Twin-Doku) | Hausbesitzer gratis; Revenue = Lead-Fee von GEAK-Experten und Installateuren |
| 10.05. (Projekt-Kontext) | Gratis-Voranalyse als Türöffner, dann GEAK via Partner, Fördergesuch-Begleitung, Installateur-Leads CHF 100–200 |
| 17.05. (Status) | „Modell D Hybrid“: B2C CHF 99–149 / 349–499, dazu B2B-Lead-Reward 5–10 %, dazu B2G ab Phase 3 |
| 19.05. | GEAK-Zulieferer-Pivot. Offen ist, wer wen bezahlt. Ein Re-Vorschlag CHF 499/990 liegt vor, aber es gibt noch keinen GEAK-Partner |

**Selbst gesetzte Meilensteine [V]:**

- erster zahlender Kunde bis KW 26 (Ende Juni 2026)
- 5 Kunden bis KW 30
- Reality-Check: „Wenn KW 30 noch 0 zahlende Kunden → Modell-Iteration“

Die Engine gilt als „fertig, eingefroren bis 5 zahlende Kunden“.

---

## 2. Was technisch existiert

### 2a. Gebäude-Analyse-Engine (das eigentliche Produkt)

| Schicht | Module | Inhalt |
|---|---|---|
| Datenbeschaffung | `gwr_client`, `adress_lookup`, `solar`, `klimadata`, `vision_analyzer`, `geak_extractor` | geo.admin SearchServer → EGID; GWR per `extendedHtmlPopup` (Regex-Parsing); 7 Layer (VEC25, BFE-Wärmenachfrage, Sonnendach, Minergie, Geothermie …); PVGIS v5.2 |
| Berechnung | `u_werte`, `heizlast`, `geak`, `verbrauch`, `hydraulik`, `muken`, `betrieb`, `vollkosten`, `oekobilanz` | U-Werte nach Baujahr-Epoche; Heizlast ΦT+ΦV (bezeichnet als SIA 384/2 / EN 12831); GEAK-Bilanz SIA 380/1 mit Klassierung nach R_H,ref = Qh/Q_H,li, Q_H,li = (16+15·GHZ)·f_T (GEAK-Normierung 2.2.0, Tab. 41); Verbrauchskalibrierung; SIA 480 Annuität (20 J., 3 %); CO₂-Pfad Strom 2024–2044 |
| Orchestrierung | `digital_twin`, `auto_kalibrierung`, `energiefuchs.py` (CLI) | Twin-Datenmodell; CLI: GWR → Fragebogen → Dossier |
| Output | `dossier.py`, `pdf_generator.py` (fpdf2) | JSON intern, Kundentext (Laien), Experten-Annex |
| Webapp | `webapp/main.py` (FastAPI, Port 8003), 5 Jinja-Templates, `landing.html` | Formular → Stripe CHF 99 → Analyse → PDF-Download |

Kalibriert ist die Engine an drei echten BE-GEAKs (GEAK Tool 6.8, Soll-Klasse E) und an einem Pilotobjekt, dem Haus des Vaters in Kanton BE/SO. Der Pilot ist noch offen: IBS-Messwerte fehlen.

### 2b. Lead-/Ideen-Pipeline (anderes Produkt unter gleichem Namen)

`main.py`, `scraper*.py`, sechs `analyzer_*`-Varianten, `swiss_filter`, `notion_writer` und `feedback_trainer` bilden eine eigene Pipeline. Sie scrapt Reddit, HN und ProductHunt, lässt ein LLM auf 0–100 scoren und schreibt Treffer ab 70 nach Notion. Die Notion-Seite „Engine — Technische Doku“ beschreibt **nur diesen Stack**, nicht die Gebäude-Engine. **Er ist funktional tot [V]:**

- Die Filter-Schnittstelle passt nicht zum Analyzer.
- Der Score erreicht in der Praxis nie ≥ 70.
- Der Feedback-Trainer wird nie aufgerufen.
- Die Lead-Dateien sind leer.

Verwendete LLMs: Claude Haiku 4.5, Sonnet 4.6, Ollama mistral, OpenRouter und ein untrainiertes torch-Modell, dessen Score faktisch zufällig ist.

---

## 3. Tatsächlicher Zustand: „fertig“ stimmt nicht [V]

Die Doku sagt „Engine fertig“. Der Code-Stand vom 26.05. widerspricht dem.

**Blocker (verhindern jeden zahlenden Kunden):**

- `dossier.py` enthält einen **SyntaxError** (verwaiste Zeilen und eine doppelte `erstelle_dossier_twin`). Deshalb scheitert der Import in Webapp und CLI.
- Wählt jemand in der Webapp Gas, Pellets oder Elektro, entsteht ein ungültiger Träger-Key und ein ValueError. Das passiert **nach** der Zahlung.
- `pdf_generator` lädt die Schrift fest aus `C:/Windows/Fonts/arial.ttf` und läuft deshalb nur unter Windows. In `requirements.txt` fehlen fastapi, uvicorn, jinja2, stripe und fpdf2.
- Es gibt keine automatisierten Tests.

**Sicherheit und Datenschutz (DSG-relevant):**

- `/verify` ohne Stripe-Session setzt `paid=True`. Die Zahlung lässt sich also umgehen.
- Schlägt die PDF-Erzeugung fehl, bekommt der Kunde als Fallback das **Dossier eines echten Kunden inklusive Name**.
- `/download/{id}` hat keine Authentifizierung, die ID ist erratbar (Zeitstempel + E-Mail).
- Klarnamen und Adressen von Kunden und GEAK-Experten stehen im Code und in `output/`, und `output/` ist nicht in `.gitignore`.
- Die Seiten AGB, Datenschutz und Disclaimer sind verlinkt, haben aber keine Route.

**Die Webapp rechnet für alle Kunden fast dasselbe:**

- Es findet kein GWR-Abruf statt.
- Die Vorlauftemperatur ist fest auf 65 °C gesetzt, deshalb ist WP-Status immer „BEDINGT“.
- Die PLZ wird nie gesetzt, deshalb gelten immer Klima Bern und Förderung BE.
- Das PDF druckt für jeden Kunden die Pilot-Empfehlung „Öl behalten + PV 6 kWp, 3'581 CHF/Jahr“.
- Der Experten-Annex behauptet fest „Δ < 20 % konsistent“ und „EBF = GWR × 1.156“, unabhängig von der Rechnung.

**Die eigene Hauptregel wird verletzt: BE-Logik gilt für alle Kantone:**

- `auto_kalibrierung` setzt `kanton="BE"` und HGT 3800 fest.
- „SL7 BE“ ist Standardoption für alle Kantone.
- Die PLZ→Kanton-Zuordnung ist fehlerhaft: Die erste Ziffer 4 wird als SO gewertet, 39xx als BE statt VS, 2500 Biel als NE, 65xx als OW.
- Förderung ist hartcodiert: BE 6000, SO 4000, sonst 3000.

**Fachliche Fehler im Kern:**

- Der Verbrauch (Endenergie) wird **ohne Kesselwirkungsgrad** gegen die Nutzwärme Qh kalibriert. Das verzerrt die U-Wert-Skalierung systematisch.
- Die Klimanormierung wirkt in die falsche Richtung (Faktor Davos 1.45).
- Die GHZ-Werte sind doppelt und widersprüchlich hinterlegt: BE 3300 in `klimadata` gegen 3800 in `geak`/`verbrauch`.
- Der CO₂-Faktor für Strom existiert in vier Varianten (0.034 / 0.040 / 0.071 / 0.128).
- `muken.fossil_codes` 7520–7550 bezeichnen laut `gwr_client` Abwärme, Elektro, Solar und Luft. Das Wort „kessel“ macht auch Holzkessel fossil.
- `vollkosten`: Die Hybrid-Option fällt in den reinen WP-Zweig.
- „GEAK D erreichbar“ wird aus der **Hüllenklasse** abgeleitet. Für die MuKEn-Befreiung zählt aber die Klasse Gesamtenergieeffizienz **[P]**.
- Die Heizlast rechnet ohne Reduktionsfaktor gegen Erdreich und Unbeheizt. Sie wird deshalb wahrscheinlich überschätzt **[P]**.
- Die Doku nennt zwei verschiedene Faustformeln für die Heizlast (÷2000 h gegen ÷1800 h Volllaststunden).

---

## 4. Rechtliche Grundlage: interner Widerspruch

Die Notion-Seite „Projekt-Kontext“ führt eine Tabelle „MuKEn 2014 — alle 9 Standardlösungen (BE)“. Dort steht **SL7 = Gebäudehülle Minergie**. Direkt darunter heisst es als „verifiziert“: **SL7 BE = Brenner + WP-Boiler + PV (5 Wp/m² EBF)**. Beides kann nicht stimmen.

**[P]:** Nach meinem Kenntnisstand kennt MuKEn 2014 (Modul Heizungsersatz, Art. 1.29 ff.) 11 Standardlösungen. Eine davon ist „WW-Wärmepumpe + PV“. Nummerierung und Umfang variieren je nach kantonaler Umsetzung. `muken.py` übernimmt die 9er-Tabelle. Das muss man gegen den **BE-Erlasstext** (KEnG / KEnV in der geltenden Fassung) prüfen, inklusive der Frage, ob und seit wann die Pflicht „GEAK D oder Standardlösung“ in BE überhaupt in Kraft ist. Die Revision 2019 ist in der Volksabstimmung gescheitert. Laut Code gilt SO als „ausstehend“ (Abstimmung Feb. 2026); dieser Stand muss aktualisiert werden.

### 4a. Architekturvorgabe für die Rechtsengine

Eine Regel ist nicht „wahr“, sondern eine **versionierte Behauptung mit Geltungsbereich und Evidenz**. „GEAK nötig?“ umfasst mindestens vier verschiedene Fragen, und die Engine darf sie nie zusammenlegen:

| Regeltyp | Beispiel |
|---|---|
| `foerdervoraussetzung_administrativ` | GEAK als Bedingung für die Auszahlung, Gesuch vor Baubeginn |
| `foerdervoraussetzung_technisch` | WPSM, Gütesiegel, Leistungsgrenzen, W/m² EBF |
| `ersatzvorschrift` | GEAK D oder Standardlösung beim Ersatz einer fossilen Heizung (Energiegesetz) |
| `gebaeudeanalyse_foerderung` | GEAK / GEAK Plus als selbst geförderte Massnahme |

**Felder pro Behauptung:** `kanton`, `massnahme` (z. B. M-05), `regeltyp`, `aussage`, `gueltig_ab`, `gueltig_bis`, `rechtsstatus` (in_kraft / entwurf / abgelehnt), `evidenzstatus` (unverifiziert / sekundär / primär / schriftlich_bestätigt), `quelle_url`, `quelle_version`, `zitat_wörtlich`, `geprueft_am`, `geprueft_von`, `entscheidungsrelevanz`.

**Harte Ausgaberegel:** Das Dossier formuliert eine Aussage nur dann als Tatsache, wenn der Evidenzstatus `primär` oder `schriftlich_bestätigt` ist **und** Kanton, Massnahme und Datum des Gebäudefalls im Geltungsbereich liegen. Sonst lautet die Ausgabe: „nicht verifiziert, vor Auftragserteilung bei der Fachstelle bestätigen“, zusammen mit der Entscheidungsrelevanz. Sekundärquellen wie Installateur-Websites oder KI-Zusammenfassungen reichen nie für eine Hochstufung.

**Fact-Gate:** Primärquelle → Extraktion mit wörtlichem Zitat → Behauptung → Geltungsbereich → Review → Freigabe → Änderungsüberwachung (Hash der Quelle; ändert sie sich, wird die Regel automatisch auf `unverifiziert` zurückgestuft). Für den Start reicht das manuell für BE und SO.

**Belegfall (26.09.2026):** Eine Review-KI hat für SO M-05 den Satz „Ohne gültigen GEAK kann der Förderbeitrag nicht ausbezahlt werden“ behauptet. Die Belege dafür waren KI-Zusammenfassungen von Suchergebnissen. Die Treffer zur Suche nach dem genauen Satz stammten von der **Energieförderung des Kantons Bern**. Der Satz ist also für BE belegt, für SO bisher nicht. Für SO ist nur die separate GEAK-Plus-Förderung nach SO-21 belegt: EFH 50 %, höchstens CHF 1'100; MFH höchstens CHF 1'800. **Nachtrag, gleicher Tag, Jans Prüfung der Primärquellen der Energiefachstelle SO:**

| Behauptung (SO, M-05) | Aussage | Evidenzstatus | Quelle |
|---|---|---|---|
| WPSM-Anlagezertifikat ≤ 15 kWth | JA | primär | Förderbedingungen Wärmepumpen V250101, FAQ |
| Leistungsgarantie > 15 kWth | JA | primär | Förderbedingungen Wärmepumpen V250101 |
| Gesuch vollständig vor Baubeginn | JA | primär | FAQ |
| GEAK als Auszahlungsbedingung | NEIN | **primär, Negativbefund** | in den WP-Förderbedingungen V250101 und M-05 ab 01.01.2024 nicht genannt |
| Grundbeitrag CHF 3'550 | – | sekundär | noch offen |

`quelle_version=250101`, `geprueft_am=2026-09-26`.

**Neuer Evidenzstatus `primär_negativ`:** Wenn eine Bedingung in der Quelle *fehlt*, belegt das nur etwas, sofern die ganze Quellenkette geprüft ist: die massnahmenspezifischen Bedingungen, die dort verwiesenen allgemeinen Förderbedingungen und das Reglement bzw. die Verordnung. Sonst gilt die Aussage nur als „in Dokument X nicht verlangt“.

---

## 5. Kernthese und Gegenargument

**These [A]:** Engine und Fachwissen sind weit genug für einen **manuell begleiteten** ersten Kunden. Die Automatisierung, also Webapp und Stripe, ist dafür nicht reif. Der Engpass ist weder technisch noch fachlich, sondern ein **ungeklärtes Geschäftsmodell**:

- Wer zahlt?
- Gibt es einen GEAK-Partner?
- Welcher Preis?

Seit dem 19.05. ist dazu nichts entschieden. KW 26 und KW 30 sind vorbei, ohne dass ein Kunde dokumentiert ist.

**Gegenargument:** Genau weil die Webapp mit Zahlungsbypass und Datenleck live gehen könnte, ist ein technischer Fix *vor* jeder Akquise Pflicht. Das ist richtig, betrifft aber nur den Self-Service-Pfad. Ein Dossier, das Jan manuell per CLI erstellt und durchsieht, umgeht diese Blocker, sobald der SyntaxError behoben ist.

**Entscheid-Vorschlag [A]:**

1. `dossier.py` reparieren.
2. Webapp offline lassen.
3. 1–3 Dossiers manuell gegen Rechnung liefern, mit einem GEAK-Experten als Bestätiger.
4. Erst danach Pricing und Webapp.

**Kill-Kriterium:** Findet sich bis Ende Q4 2026 kein GEAK-Experte, der das Dossier als Input akzeptiert *und* dafür (oder für den Lead) zahlt oder den Kundenpreis mitträgt, dann trägt das Zulieferer-Modell nicht. Dann bleibt nur B2C-Voranalyse ohne Zertifikatsbezug.

---

## 6. Prüfauftrag für die zweite KI

Bitte prüfe diese Punkte kritisch und mit Quellen:

1. **MuKEn / Kanton BE:** Welche Standardlösungen gelten aktuell in BE (Erlass, Artikel, Inkrafttreten)? Ist „SL7 = WP-Boiler + PV 5 Wp/m² EBF“ korrekt? Gilt „GEAK D“ als Befreiung, und wenn ja, welche GEAK-Klasse ist gemeint (Hülle oder Gesamt)? Wie ist der Stand in SO nach der Abstimmung 2026?
2. **Methodik:** Ist die Kalibrierung „Endenergie-Verbrauch → Qh → U-Wert-Skalierung“ zulässig, und wie ist der Kesselwirkungsgrad korrekt einzubeziehen? Wie gross ist der Fehler von Heizlast nach vereinfachter EN 12831 gegenüber SIA 384/2 bzw. 384.201? Ist EBF = GWR-Wohnfläche × 1.15 vertretbar?
3. **Haftung:** Ist ein Remote-Vor-GEAK mit U-Werten aus Baujahr-Tabellen als „rechtssicher“ vermarktbar? Welche Disclaimer braucht es, und ist die geplante Berufshaftpflicht (CHF 300–600/Jahr) realistisch?
4. **Geschäftsmodell:** Hat ein GEAK-Experte einen ökonomischen Anreiz, ein fremdes Dossier zu „bestätigen“? Welche Reglemente (GEAK-Expertenpflichten, Begehungspflicht) stehen dem entgegen?
5. **Markt:** Gibt es neben erneuerbarheizen.ch (BFE), der Suissetec-App, Eturnity und energiefranken.ch weitere Wettbewerber für eine B2C-Voranalyse?
6. **Widerspruch in der Positionierung:** „Optionsdarstellung, kein Empfehlungstool“, aber auch „Lead-Verkauf an Installateure“. Ist die Neutralität glaubwürdig?

Ergänzend zum Code: Das Repomix-Pack liegt auf Google Drive (`energiefuchs-context.md`, 26.05.2026). **Vor der Weitergabe an Dritte müssen Klarnamen und Adressen daraus entfernt werden.**
