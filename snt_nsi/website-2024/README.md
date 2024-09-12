# Site web

Nouvelle version du site web pour l'année scolaire 2023-2024.

# Documentation

- [MKDocs](https://www.mkdocs.org/)
- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Markdown extensions](https://facelessuser.github.io/pymdown-extensions/)

## Développement
Lancement du serveur de développement :

```bash
(cd src ; mkdocs serve)
```

## Déploiement

Le site web est hébergé sur Vercel.
Le déploiement s'effectue automatiquement dès lors qu'une nouvelle est version poussée sur la branche `main`.

### Configuration Vercel

Les paramètres de build et de déploiement sont les suivants :

| Paramètre        | Valeur                             |
|------------------|------------------------------------|
| Framework Preset | Other                              |
| Root Directory   | `src`                              |
| Build Command    | `mkdocs build`                     |
| Output Directory | `site`                             |
| Install Command  | `pip3 install -r requirements.txt` |

### Points d'attentions

Avant tout déploiement, s'assurer que le fichier `requirements.txt` soit bien à jour.
Pour celà, lancer la commande ci-dessous depuis la racine du projet :

```bash
poetry export --without-hashes > src/requirements.txt
```