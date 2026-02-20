# 🤖 Projet NSI BOT DISCORD : Bot Discord Modulaire (Python)

## 📌 Présentation du Projet
Ce projet est un bot Discord développé en Python avec **discord.py 2.x**.  
L’objectif est de proposer un bot **simple, stable et propre** : une architecture modulaire, une configuration validée au démarrage, des logs clairs, et des commandes utiles pour un serveur.

Le dépôt inclut aussi un **site web de présentation + documentation**, hébergé via **GitHub Pages**.

Site / Documentation :
- https://antoninche.github.io/bot_discord/

---

## 🚀 Fonctionnalités Détaillées

### 🛡️ Administration
* **Ping (latence)** :
  * `!ping` et `/ping` : affiche la latence du bot en millisecondes.
* **Nettoyage de salon (purge)** :
  * `!purge [limit]` et `/purge limit:<n>` : supprime les derniers messages du salon.
  * `limit` est borné entre **1 et 200** (défaut : 10).
  * En version préfixée, le bot supprime aussi le message de commande (purge `limit + 1`).
  * La confirmation s’auto-supprime après quelques secondes.
* **Sécurité** :
  * Les commandes sensibles sont réservées aux utilisateurs ayant la permission Discord **Administrateur**.

### 🎲 Divertissement
* **Lancer un dé** :
  * `!roll [faces]` et `/roll faces:<n>` : tire un nombre aléatoire entre 1 et `faces`.
  * `faces` est borné entre **2 et 1000** (défaut : 6).
  * En slash, la réponse est **éphémère** (visible uniquement par l’utilisateur).

### 🏷️ Gestion des rôles
* **Ajouter un rôle à l’auteur** :
  * `!addrole <nom_du_role>` : ajoute un rôle à l’auteur de la commande.
  * Recherche de rôle insensible à la casse (nom exact).
* **Retirer un rôle à l’auteur** :
  * `!removerole <nom_du_role>` : retire le rôle à l’auteur.
* **Sécurité** :
  * Ces commandes sont réservées aux **Administrateurs**.

### 🔊 Vocal
* **Rejoindre un salon vocal** :
  * `!join` : le bot rejoint le salon vocal où se trouve l’auteur (ou s’y déplace s’il est déjà connecté ailleurs).
* **Quitter le salon vocal** :
  * `!leave` : déconnecte le bot du vocal.
* **Contrôles** :
  * Le bot refuse la commande si l’utilisateur n’est pas en vocal, ou s’il n’est pas connecté lors de `!leave`.

---

## 🧠 Fonctionnement Interne 
* **Architecture modulaire** : chaque domaine est isolé (admin, fun, rôles, vocal).
* **Chargement automatique des modules** au démarrage.
* **Configuration validée** : le bot lit `config.json` et vérifie les champs et types.
* **Logs normalisés** : format stable (date, niveau, module, message) pour diagnostiquer rapidement.
* **Synchronisation des slash commands** :
  * Sync globale (par défaut) ou sync sur un serveur de dev si `guild_id_for_dev_sync` est renseigné.

---

## 🛠️ Stack Technique
* **Langage** : Python (3.10+ recommandé)
* **Lib Discord** : discord.py 2.x
* **Configuration** : fichier `config.json` (validation stricte)
* **Logs** : module `logging` (format unifié)
* **Site** : HTML/CSS (GitHub Pages)

---

## 📂 Structure du Projet
```text
bot_discord/
│
├── bot/
│   ├── __main__.py          # Point d’entrée : python -m bot
│   ├── bot.py               # Création du bot + chargement modules + sync slash
│   ├── admin.py             # Commandes admin (ping, purge) + slash
│   ├── fun.py               # Commandes fun (roll) + slash
│   ├── roles.py             # Gestion rôles (addrole, removerole)
│   ├── music.py             # Vocal (join, leave)
│   ├── config.py            # Lecture + validation config.json
│   ├── logging_config.py    # Configuration des logs
│   └── checks.py            # Checks réutilisables (admin)
│
├── docs/                    # Site GitHub Pages (présentation + documentation)
│   ├── index.html
│   ├── documentation.html
│   └── styles.css
│
├── config.json              # Configuration (token, prefix, logs, sync)
├── requirements.txt         # Dépendances Python
└── README.md
```
---

## 🛠️ Installation des dépendances

Avant de lancer le projet, installez les bibliothèques nécessaires à l'aide du fichier `requirements.txt` :

```bash
pip install -r requirements.txt 
