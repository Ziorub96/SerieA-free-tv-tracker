import json
import os
import importlib

from scrapers.seriea import get_matches
from scrapers.utils import match_game


# ---------------------------------------------------------------
# DEBUG MODE
# Attivalo con: DEBUG_SCRAPERS=1 python main.py
# ---------------------------------------------------------------
DEBUG = os.environ.get("DEBUG_SCRAPERS") == "1"


# ---------------------------------------------------------------
# MAPPA BROADCASTER
# (nome_modulo, lingua, affidabile)
# ---------------------------------------------------------------
BROADCASTER_MAP = {
    # YouTube (affidabili)
    "CazéTV (YouTube)":    ("cazetv_youtube",    "pt", True),
    "SportyNet (YouTube)": ("sportynet_youtube", "pt", True),
    # Siti diretti
    "XSports":             ("xsports",           "pt", False),
    "SportyTV":            ("sportytv",          "en", True),
    "CBS Sports Golazo":   ("golazo",            "en", True),
    "Telemundo":           ("telemundo",         "es", False),
    "ANTV":                ("antv",              "id", True),
    "Match TV (free)":     ("matchtv",           "ru", False),
    "New World TV":        ("newworld",          "fr", False),
    "ELTA":                ("elta",              "zh", False),
    # Aggregatore
    "LiveSoccerTV":        ("livesoccertv",      "en", True),
}


def safe_import(module_name, func_name="get_schedule"):
    """
    Importa un modulo scraper in modo sicuro.
    Se il file non esiste o ha errori, restituisce None e logga un warning.
    """
    try:
        module = importlib.import_module(f"scrapers.{module_name}")
        func = getattr(module, func_name, None)
        if func is None:
            print(f"  [WARNING] Funzione {func_name}() mancante in scrapers/{module_name}.py")
        return func
    except ModuleNotFoundError:
        print(f"  [WARNING] Modulo mancante: scrapers/{module_name}.py")
        return None
    except Exception as e:
        print(f"  [WARNING] Errore importando scrapers/{module_name}.py: {e}")
        return None


def debug_preview(name, pages, max_items=3, max_chars=200):
    """Stampa un'anteprima dei primi elementi recuperati da uno scraper."""
    if not DEBUG:
        return
    print(f"    → {name}: {len(pages)} elementi")
    for i, p in enumerate(pages[:max_items]):
        preview = p[:max_chars].replace("\n", " ").replace("\r", " ")
        print(f"      [{i}] ({len(p)} char) {preview}")


def main():
    print("=" * 60)
    print("  Serie A Free TV Tracker")
    if DEBUG:
        print("  *** DEBUG MODE ATTIVO ***")
    print("=" * 60)

    # ---------------------------------------------------------
    # 1. CALENDARIO
    # ---------------------------------------------------------
    print("\n[1/4] Recupero calendario Serie A...")
    try:
        matches = get_matches(days_ahead=10)
    except Exception as e:
        print(f"  [ERRORE] Impossibile recuperare il calendario: {e}")
        return

    print(f"  → {len(matches)} partite nei prossimi 10 giorni.")

    if not matches:
        print("  [WARNING] Nessuna partita trovata nel calendario.")
        return

    # ---------------------------------------------------------
    # 2. PALINSESTI
    # ---------------------------------------------------------
    print("\n[2/4] Recupero palinsesti dai broadcaster...")
    sources = {}

    for name, (module, lang, affidabile) in BROADCASTER_MAP.items():
        func = safe_import(module)
        if func is None:
            continue

        try:
            pages = func()
            sources[name] = {
                "pages": pages,
                "lang": lang,
                "affidabile": affidabile
            }
            status = "✅" if pages else "⚠️"
            print(f"  {status} {name}: {len(pages)} elementi recuperati.")
            debug_preview(name, pages)
        except Exception as e:
            print(f"  ❌ {name}: ERRORE - {e}")
            sources[name] = {
                "pages": [], "lang": lang, "affidabile": affidabile
            }

    if not sources:
        print("\n[FATAL] Nessuno scraper disponibile.")
        return

    # ---------------------------------------------------------
    # 3. MATCHING
    # ---------------------------------------------------------
    print("\n[3/4] Matching partite ↔ broadcaster...")
    report = []
    partite_con_match = 0

    for match in matches:
        channels = []
        da_verificare = []

        for source_name, data in sources.items():
            for page in data["pages"]:
                try:
                    if match_game(page, match["home"], match["away"], lang=data["lang"]):
                        if data["affidabile"]:
                            if source_name not in channels:
                                channels.append(source_name)
                        else:
                            if source_name not in da_verificare:
                                da_verificare.append(source_name)

                        if DEBUG:
                            snippet = page[:150].replace("\n", " ")
                            print(f"      MATCH: {source_name} → {snippet}")

                        break
                except Exception as e:
                    if DEBUG:
                        print(f"      [errore matching {source_name}]: {e}")

        report.append({
            **match,
            "channels": channels,
            "canali_da_verificare": da_verificare
        })

        if channels or da_verificare:
            partite_con_match += 1
            print(f"  ✅ {match['home']} - {match['away']}: "
                  f"{', '.join(channels) if channels else '—'} "
                  f"| da verificare: {', '.join(da_verificare) if da_verificare else '—'}")

    # ---------------------------------------------------------
    # 4. OUTPUT
    # ---------------------------------------------------------
    print("\n[4/4] Generazione report...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # JSON
    with open("data/report.json", "w", encoding="utf8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Markdown
    with open("output/report.md", "w", encoding="utf8") as f:
        f.write("# Serie A Free TV Report\n\n")
        f.write("*Partite nei prossimi 10 giorni — aggiornato automaticamente*\n\n")

        for row in report:
            f.write(f"## {row['home']} - {row['away']}\n")
            f.write(f"**Data:** {row['date']} ore {row['time']}\n\n")

            if row["channels"]:
                f.write("### ✅ Emittenti gratuite confermate:\n")
                for c in row["channels"]:
                    f.write(f"- {c}\n")

            if row["canali_da_verificare"]:
                f.write("\n### ⚠️ Da verificare manualmente:\n")
                for c in row["canali_da_verificare"]:
                    f.write(f"- {c}\n")

            if not row["channels"] and not row["canali_da_verificare"]:
                f.write("- nessuna emittente trovata\n")

            f.write("\n---\n\n")

    # Summary finale
    print(f"\n  → {partite_con_match}/{len(report)} partite con almeno un'emittente trovata.")
    print("  → Report: data/report.json, output/report.md")

    if DEBUG:
        print("\n  [DEBUG] Riepilogo sorgenti:")
        for name, data in sources.items():
            print(f"    - {name}: {len(data['pages'])} elementi")

    print("=" * 60)


if __name__ == "__main__":
    main()