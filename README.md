# Serie A Free TV Tracker

Tracker delle partite di Serie A trasmesse **gratuitamente** (free-to-air, FAST o YouTube) nel mondo — stagione 2026/27.

## Broadcaster supportati

| Broadcaster | Territorio | Tipo | Affidabilità |
|---|---|---|---|
| CazéTV | Brasile | YouTube | ✅ Alta |
| SportyNet | Brasile | YouTube | ✅ Alta |
| XSports | Brasile | Free-to-air | ⚠️ Bassa |
| SportyTV | Africa subsahariana | App gratuita | ✅ Alta |
| CBS Sports Golazo | USA | FAST | ✅ Alta |
| Telemundo | USA (spagnolo) | Free-to-air OTA | ⚠️ Media |
| ANTV | Indonesia | Free-to-air | ✅ Alta |
| Match TV | Russia | Free-to-air | ⚠️ Media |
| New World TV | Africa francofona | Free parziale | ⚠️ Bassa |
| ELTA | Taiwan | OTT freemium | ⚠️ Bassa |
| **LiveSoccerTV** | **Globale** | **Aggregatore** | ✅ Alta |

## ⚠️ Geoblocking

Ogni broadcaster trasmette gratuitamente **solo nel proprio territorio**.

## Installazione

```bash
pip install -r requirements.txt
playwright install chromium
python main.py