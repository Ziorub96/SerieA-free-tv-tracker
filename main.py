"""
Motore principale del tracker.

Pipeline:
  1. Scarica il calendario completo della Serie A (scrapers/seriea.py)
  2. Scarica il "palinsesto" (video recenti o HTML) di ogni broadcaster
     gratuito configurato (scrapers/youtube_broadcasters.py + web_broadcasters.py)
  3. Per ogni partita, cerca corrispondenze fuzzy nel testo di ogni broadcaster
  4. Salva un report strutturato (data/report.json) e uno leggibile
     (output/report.md), distinguendo broadcaster affidabili da quelli
     "da verificare manualmente"
"""

import json
import os
from datetime import datetime, timezone

import config
from utils.logging_config import setup_logging
from utils.matching import match_game
from scrapers.seriea import get_matches
from scrapers.youtube_broadcasters import get_all_youtube_sources
from scrapers.web_broadcasters import get_all_web_sources

logger = setup_logging()


def build_report(matches: list[dict], sources: dict) -> list[dict]:
    report = []
    for match in matches:
        channels = []
        canali_da_verificare = []

        for source_name, data in sources.items():
            found = any(
                match_game(page, match["home"], match["away"], lang=data["lang"])
                for page in data["pages"]
            )
            if not found:
                continue
            if data["affidabile"]:
                channels.append(source_name)
            else:
                canali_da_verificare.append(source_name)

        report.append(
            {
                **match,
                "channels": sorted(channels),
                "canali_da_verificare": sorted(canali_da_verificare),
            }
        )
    return report


def filter_upcoming(matches: list[dict]) -> list[dict]:
    if not config.ONLY_UPCOMING_MATCHES:
        return matches
    now = datetime.now(timezone.utc)
    upcoming = []
    for match in matches:
        try:
            match_dt = datetime.fromisoformat(match["datetime_iso"].replace("Z", "+00:00"))
        except ValueError:
            upcoming.append(match)  # in dubbio, meglio non escluderla
            continue
        if match_dt >= now:
            upcoming.append(match)
    return upcoming


def write_json_report(report: list[dict]) -> None:
    os.makedirs(config.DATA_DIR, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matches": report,
    }
    with open(config.REPORT_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def write_markdown_report(report: list[dict]) -> None:
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# Serie A Free TV Report",
        "",
        f"_Aggiornato il {generated_at}_",
        "",
        (
            "> Ogni broadcaster trasmette gratuitamente solo nel proprio territorio: "
            "questo report indica dove la partita è disponibile gratis, non che sia "
            "visibile da qualsiasi paese."
        ),
        "",
    ]

    if not report:
        lines.append(
            "**Nessuna partita trovata.**\n\n"
            "Possibili cause:\n"
            "- L'API ESPN ha restituito 403 (blocco dei runner di GitHub Actions)\n"
            "- Nessuna partita futura nel periodo configurato\n"
            "- Errore di rete temporaneo\n\n"
            "Controlla i log di GitHub Actions per i dettagli."
        )
    else:
        for row in report:
            lines.append(f"## {row['home']} - {row['away']}")
            lines.append(f"Data: {row['date']} ore {row['time']} (UTC)")
            lines.append("")

            if row["channels"]:
                lines.append("### ✅ Emittenti gratuite confermate")
                lines.extend(f"- {c}" for c in row["channels"])
            else:
                lines.append("Nessuna emittente gratuita confermata al momento.")

            if row["canali_da_verificare"]:
                lines.append("")
                lines.append("### ⚠️ Da verificare manualmente (possibili pay/freemium)")
                lines.extend(f"- {c}" for c in row["canali_da_verificare"])

            lines.append("")
            lines.append("---")
            lines.append("")

    with open(config.REPORT_MD_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def main():
    logger.info("Avvio Serie A Free TV Tracker")

    matches = get_matches()
    matches = filter_upcoming(matches)
    logger.info("%d partite da coprire (dopo filtro date).", len(matches))

    sources = {}
    sources.update(get_all_youtube_sources())
    sources.update(get_all_web_sources())

    report = build_report(matches, sources)

    write_json_report(report)
    write_markdown_report(report)

    confirmed = sum(1 for r in report if r["channels"])
    logger.info(
        "Fatto: %d/%d partite con almeno un'emittente confermata. "
        "Report in %s e %s",
        confirmed,
        len(report),
        config.REPORT_JSON_PATH,
        config.REPORT_MD_PATH,
    )


if __name__ == "__main__":
    main()