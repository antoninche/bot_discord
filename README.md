# Bot Discord

Bot Discord en Python basé sur discord.py 2.x, organisé en cogs, avec configuration via fichier JSON.

## Installation

1) Créer un environnement virtuel
- Windows:
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
- macOS/Linux:
  - `python3 -m venv .venv`
  - `source .venv/bin/activate`

2) Installer les dépendances
- `pip install -r requirements.txt`

## Configuration

Éditer `config.json` et renseigner `token`.

## Lancement

- `python -m bot`

## Structure

- `bot/bot.py` : création du bot + chargement des cogs
- `bot/cogs/` : fonctionnalités (admin, fun, roles, music)
- `bot/config.py` : lecture/validation de `config.json`
- `bot/logging_config.py` : configuration des logs
