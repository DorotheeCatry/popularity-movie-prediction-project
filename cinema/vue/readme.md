# Trailer Scraper

Ce projet contient un spider Scrapy utilisant Playwright pour extraire les bandes‑annonces des prochaines sorties ciné sur Allociné.

## Structure du projet

```
trailer/                # racine du projet Scrapy
├── scrapy.cfg           # configuration globale de Scrapy
└── trailer/             # module Python
    ├── items.py         # définition des items Scrapy
    ├── middlewares.py   # rotation d'User-Agent
    ├── pipelines.py     # nettoyage des items (vues, date)
    ├── settings.py      # configuration Scrapy & Playwright
    └── spiders/         # répertoire des spiders
        └── trailerspider.py  # spider principal
```

## Prérequis

- Python >= 3.8
- Node.js (pour Playwright)

## Installation

1. Cloner le dépôt et positionner le terminal à la racine du dossier `trailer/` :
   ```bash
   git clone <url-du-repo>
   cd trailer
   ```

2. Créer un environnement virtuel et l'activer :
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS/Linux
   .\.venv\Scripts\activate  # Windows
   ```

3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Installer les navigateurs Playwright :
   ```bash
   playwright install
   ```

## Usage

- Lancer le spider :
  ```bash
  scrapy crawl trailerspider -L INFO
  ```
  Les résultats sont exportés dans `trailers.csv` (colonnes : `titre`, `vues`, `date_sortie`).

## Personnalisation

- **Settings**
  - `DOWNLOAD_DELAY`, `AUTOTHROTTLE_...` : gestion du throttling
  - `USER_AGENT_LIST` : liste des User‑Agents
  - Playwright (`PLAYWRIGHT_BROWSER_TYPE`, `PLAYWRIGHT_LAUNCH_OPTIONS`)
  - Pipelines & Feeds

- **Spider**
  - URL de départ dans `start_urls`
  - Sélecteurs CSS dans `parse_list` et `parse_detail`
  - Filtre sur la sortie du mercredi suivant

## Débogage

- Mode debug :
  ```bash
  scrapy crawl trailerspider -L DEBUG
  ```
- Vérifier la présence de Playwright dans la sortie :
  ```text
  [scrapy-playwright] INFO: Browser chromium launched
  ```

## Licence

MIT © Ton Nom

