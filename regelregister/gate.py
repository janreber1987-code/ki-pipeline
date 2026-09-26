"""Fact-Gate: prüft das Regelregister und liefert die für ein Dossier zulässige Aussage."""
import json
import sys
from pathlib import Path

REGELTYPEN = {
    "foerdervoraussetzung_administrativ",
    "foerdervoraussetzung_technisch",
    "ersatzvorschrift",
    "gebaeudeanalyse_foerderung",
}
EVIDENZ = {"unverifiziert", "sekundär", "primär", "primär_negativ", "schriftlich_bestätigt"}
PFLICHT_FUER_PRIMAER = ("quelle_url", "quelle_version", "zitat_woertlich", "geprueft_am")


def fehler(regel):
    f = []
    if regel["regeltyp"] not in REGELTYPEN:
        f.append(f"unbekannter regeltyp {regel['regeltyp']}")
    if regel["evidenzstatus"] not in EVIDENZ:
        f.append(f"unbekannter evidenzstatus {regel['evidenzstatus']}")
    if regel["evidenzstatus"] in ("primär", "primär_negativ", "schriftlich_bestätigt"):
        f += [f"{k} fehlt" for k in PFLICHT_FUER_PRIMAER if not regel.get(k)]
    if regel["evidenzstatus"] == "primär_negativ" and regel.get("wert") == "NEIN":
        f.append("primär_negativ darf nie NEIN sein")
    return f


def dossier_aussage(regel):
    """Nur vollständig belegte Regeln werden als Tatsache formuliert."""
    if fehler(regel) or regel["evidenzstatus"] in ("unverifiziert", "sekundär"):
        return f"{regel['aussage']}: nicht verifiziert – vor Auftragserteilung bei der Fachstelle bestätigen."
    if regel["evidenzstatus"] == "primär_negativ":
        return (f"{regel['aussage']}: in {', '.join(regel['geprueft_umfang'])} nicht als Voraussetzung "
                f"aufgeführt (Stand {regel['geprueft_am']}).")
    return f"{regel['aussage']}: {regel['wert']} (Quelle {regel['quelle_version']}, Stand {regel['geprueft_am']})."


if __name__ == "__main__":
    ok = True
    for datei in sys.argv[1:] or Path(__file__).parent.glob("regeln_*.json"):
        for regel in json.loads(Path(datei).read_text(encoding="utf-8")):
            f = fehler(regel)
            ok &= not f
            print(f"{'OK ' if not f else 'GESPERRT'} {regel['id']}: {'; '.join(f) or '-'}")
            print(f"    → {dossier_aussage(regel)}")
    sys.exit(0 if ok else 1)
