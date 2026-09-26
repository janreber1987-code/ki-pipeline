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
        pflicht = PFLICHT_FUER_PRIMAER
        if regel["evidenzstatus"] == "primär_negativ":  # Abwesenheit hat kein Zitat, dafür geprueft_umfang
            pflicht = tuple(k for k in pflicht if k != "zitat_woertlich")
        f += [f"{k} fehlt" for k in pflicht if not regel.get(k)]
    if regel["evidenzstatus"] == "primär_negativ":
        if regel.get("wert") == "NEIN":
            f.append("primär_negativ darf nie NEIN sein")
        umfang = regel.get("geprueft_umfang") or []
        if not umfang:
            f.append("geprueft_umfang fehlt")
        offen = [d["dokument"] for d in umfang if not d.get("vollstaendig_geprueft")]
        if offen:
            f.append("nicht vollständig geprüft: " + ", ".join(offen))
    return f


def dossier_aussage(regel):
    """Nur vollständig belegte Regeln werden als Tatsache formuliert."""
    if fehler(regel) or regel["evidenzstatus"] in ("unverifiziert", "sekundär"):
        return f"{regel['aussage']}: nicht verifiziert – vor Auftragserteilung bei der Fachstelle bestätigen."
    if regel["evidenzstatus"] == "primär_negativ":
        return (f"{regel['aussage']}: in {', '.join(d['dokument'] for d in regel['geprueft_umfang'])} nicht als Voraussetzung "
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
