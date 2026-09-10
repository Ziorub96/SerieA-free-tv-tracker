import json
import os

from scrapers.seriea import get_matches
from scrapers.cazetv_youtube import get_schedule as cazetv_yt
from scrapers.sportynet_youtube import get_schedule as sportynet_yt
from scrapers.xsports import get_schedule as xsports
from scrapers.sportytv import get_schedule as sportytv
from scrapers.golazo import get_schedule as golazo
from scrapers.telemundo import get_schedule as telemundo
from scrapers.antv import get_schedule as antv
from scrapers.matchtv import get_schedule as matchtv
from scrapers.newworld import get_schedule as newworld
from scrapers.elta import get_schedule as elta
from scrapers.livesoccertv import get_schedule as livesoccertv
from scrapers.utils import match_game


# Broadcaster gratuiti con configurazione
BROADCASTERS = {
    # YouTube (affidabili)
    "CazéTV (YouTube)":      {"func": cazetv_yt,    "lang": "pt", "affidabile": True},
    "SportyNet (YouTube)":   {"func": sportynet_yt, "lang": "pt", "affidabile": True},
    # Siti diretti
    "XSports":               {"func": xsports,      "lang": "pt", "affidabile": False},
    "SportyTV":              {"func": sportytv,     "lang": "en", "affidabile": True},
    "CBS Sports Golazo":     {"func": golazo,       "lang": "en", "affidabile": True},
    "Telemundo":             {"func": telemundo,    "lang": "es", "affidabile": False},
    "ANTV":                  {"func": antv,         "lang": "id", "affidabile": True},
    "Match TV (free)":       {"func": matchtv,      "lang": "ru", "affidabile": False},
    "New World TV":          {"func": newworld,     "lang": "fr", "affidabile": False},
    "ELTA":                  {"func": elta,         "lang": "zh", "affidabile": False},
    # Aggregatore
    "LiveSoccerTV":          {"func": livesoccertv, "lang": "en", "affidabile": True},
}


def main():
    print("=" * 60)
    print("  Serie A Free TV Tracker")
    print("=" * 60)

    # 1. Calendario
    print("\n[1/4] Recupero calendario Serie A...")
    matches = get_matches(days_ahead=10)
    print(f"  → {len(matches)} partite nei prossimi 10 giorni.")

    # 2. Palinsesti
    print("\n[2/4] Recupero palinsesti dai broadcaster...")
    sources = {}
    for name, config in BROADCASTERS.items():
        try:
            pages = config["func"]()
            sources[name] = {
                "pages": pages,
                "lang": config["lang"],
                "affidabile": config["affidabile"]
            }
            print(f"  {name}: {len(pages)} elementi recuperati.")
        except Exception as e:
            print(f"  {name}: ERRORE - {e}")
            sources[name] = {
                "pages": [], "lang": config["lang"],
                "affidabile": config["affidabile"]
            }

    # 3. Matching
    print("\n[3/4] Matching partite ↔ broadcaster...")
    report = []
    for match in matches:
        channels = []
        da_verificare = []

        for source_name, data in sources.items():
            for page in data["pages"]:
                if match_game(page, match["home"], match["away"], lang=data["lang"]):
                    if data["affidabile"]:
                        channels.append(source_name)
                    else:
                        da_verificare.append(source_name)
                    break

        report.append({
            **match,
            "channels": channels,
            "canali_da_verificare": da_verificare
        })

        if channels or da_verificare:
            print(f"  ✅ {match['home']} - {match['away']}: "
                  f"{', '.join(channels)} | da verificare: {', '.join(da_verificare)}")

    # 4. Output
    print("\n[4/4] Generazione report...")
    os.makedirs("data", exist_ok=True)
    os.makedirs("output", exist_ok=True)

    # JSON
    with open("data/report.json", "w", encoding="utf8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Markdown
    with open("output/report.md", "w", encoding="utf8") as f:
        f.write("# Serie A Free TV Report\n\n")
        f.write(f"*Partite nei prossimi 10 giorni — aggiornato automaticamente*\n\n")

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

    totale = sum(1 for r in report if r["channels"] or r["canali_da_verificare"])
    print(f"\n  → {totale}/{len(report)} partite con almeno un'emittente trovata.")
    print("  → Report: data/report.json, output/report.md")
    print("=" * 60)


if __name__ == "__main__":
    main()