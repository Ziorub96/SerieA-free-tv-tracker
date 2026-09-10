# Serie A Free TV Tracker

Tracker delle partite di Serie A trasmesse **gratuitamente** (free-to-air, FAST o YouTube) nel mondo — stagione 2026/27.

## Cosa cambia rispetto alla versione precedente

- **Calendario completo, non solo la giornata corrente**: l'endpoint ESPN usato in precedenza restituiva solo le partite della settimana in corso; ora viene paginato per l'intera stagione (`config.SEASON_START` → `config.SEASON_END`).
- **Meno codice duplicato**: gli 8 scraper "web" quasi identici sono diventati un'unica funzione pilotata da `config.WEB_BROADCASTERS`; stesso discorso per i canali YouTube.
- **Nessun ID YouTube "misterioso"**: se un `channel_id` non è verificato, viene risolto automaticamente dall'handle (`@nome`) invece di rischiare di scaricare il canale sbagliato.
- **Retry e timeout centralizzati**: una sessione HTTP condivisa ritenta automaticamente su errori di rete/5xx invece di fallire silenziosamente.
- **Matching più robusto**: normalizzazione degli accenti prima del confronto fuzzy.
- **Solo partite future** nel report finale (configurabile).
- **Logging vero** invece di `except: pass` silenziosi: gli errori dei singoli broadcaster sono visibili nei log di GitHub Actions ma non bloccano l'esecuzione degli altri.

## Struttura del progetto

```
seriea-free-tv-tracker/
├── .github/workflows/update.yml   # esecuzione automatica ogni 6 ore
├── config.py                      # tutta la configurazione stagionale
├── main.py                        # pipeline: calendario → scraping → matching → report
├── scrapers/
│   ├── base.py                    # sessione HTTP con retry/backoff
│   ├── seriea.py                  # calendario Serie A (ESPN API)
│   ├── youtube_utils.py           # risoluzione handle → channel_id, lettura feed RSS
│   ├── youtube_broadcasters.py    # CazéTV, SportyNet
│   └── web_broadcasters.py        # XSports, SportyTV, Golazo, Telemundo, ANTV, Match TV, New World, ELTA
├── utils/
│   ├── matching.py                # fuzzy matching + traduzioni squadre
│   └── logging_config.py
├── data/report.json               # output strutturato
├── output/report.md               # output leggibile
└── requirements.txt
```

## Broadcaster gratuiti tracciati

| Broadcaster | Territorio | Tipo | Affidabilità |
|---|---|---|---|
| CazéTV | Brasile | YouTube | ✅ Alta |
| SportyNet | Brasile | YouTube (sub-licenza ESPN) | ✅ Alta |
| CBS Sports Golazo | USA | FAST (Pluto TV, Samsung TV Plus) | ✅ Alta |
| XSports | Brasile | Free-to-air (canale 32 San Paolo) | ⚠️ Da verificare |
| SportyTV | Africa subsahariana | App gratuita | ⚠️ Da verificare |
| Telemundo | USA (spagnolo) | Free-to-air via antenna OTA | ⚠️ Da verificare |
| ANTV | Indonesia | Free-to-air | ⚠️ Da verificare |
| Match TV | Russia | Free-to-air (canale federale) | ⚠️ Da verificare |
| New World TV | Africa francofona | Prevalentemente pay | ⚠️ Da verificare |
| ELTA | Taiwan | OTT freemium | ⚠️ Da verificare |

I broadcaster marcati "Da verificare" compaiono nel report in una sezione separata: lo scraper trova un riscontro testuale, ma il modello di business del broadcaster (geoblocking severo, offerta pay/free mista) rende il match meno affidabile — vanno controllati a occhio prima di fidarsene.

## ⚠️ Limiti noti (da leggere prima di fidarti del 100% del report)

1. **Siti con palinsesto generato via JavaScript**: alcuni broadcaster (es. Telemundo, ELTA) pubblicano l'orario delle partite tramite JavaScript lato client. Uno scraping HTTP semplice (`requests.get`) vede solo l'HTML iniziale e potrebbe non trovare nulla da matchare. Se uno di questi broadcaster risulta sempre vuoto, è il sintomo — la soluzione è migrare quello scraper a Playwright (browser headless), non presente in questa versione per tenere le dipendenze leggere.
2. **URL non tutti verificati manualmente**: gli URL di New World TV ed ELTA in `config.py` sono i più plausibili trovati, ma questi due broadcaster non hanno una fonte ufficiale chiara sulla quota di partite gratuite — trattali sempre come "da verificare".
3. **Tabella traduzioni squadre da aggiornare ogni stagione**: `utils/matching.py` contiene i nomi delle 20 squadre di Serie A in spagnolo/francese/russo. Se una squadra sale o retrocede, aggiorna quella tabella, altrimenti il matching per quella squadra sui broadcaster non anglofoni fallirà silenziosamente (tornerà solo nella lista "channels" se il fuzzy matching sul nome originale basta).
4. **Geoblocking**: ogni broadcaster trasmette gratis solo nel proprio territorio. Il tracker indica *dove* la partita è visibile gratuitamente, non che lo sia da qualsiasi paese.

## Installazione e uso locale

```bash
pip install -r requirements.txt
python main.py
```

## Output

- `data/report.json` — dati strutturati, con timestamp di generazione
- `output/report.md` — report leggibile, con partite ordinate cronologicamente e broadcaster divisi tra "confermati" e "da verificare"

## Configurazione

Tutti i parametri che vanno rivisti a ogni stagione (date campionato, canali YouTube, URL broadcaster) sono centralizzati in `config.py`, con commenti su cosa aggiornare e perché.

## Prossimi passi possibili

1. Migrare a Playwright gli scraper dei siti JavaScript-heavy (Telemundo, ELTA, ANTV).
2. Aggiungere un IP di test per-territorio (header `X-Forwarded-For`) per verificare il geoblocking reale.
3. Notifiche Telegram con il report generato.
4. Estendere la tabella traduzioni a cinese (`zh`), vietnamita (`vi`).
