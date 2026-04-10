# 06 — Gestione del progetto open source su GitHub

Questo documento è separato dal resto perché tratta gli **aspetti non tecnici** che spesso decidono il successo di un progetto open source: come si presenta, come accoglie i contributi, come si governa.

---

## 1. Scegliere e dichiarare la licenza

- File `LICENSE` nella root, contenente il testo integrale di **AGPL-3.0**.
- Header di licenza nei file sorgente principali (template breve di poche righe con riferimento al file LICENSE).
- Nel `README.md` un badge della licenza e una riga che la spiega in linguaggio umano.
- Nel `pyproject.toml` il campo `license`.

Risorsa: [choosealicense.com](https://choosealicense.com/) per spiegare la scelta in modo chiaro.

---

## 2. README curato

Il README è la prima cosa che vede un visitatore. Deve rispondere in 30 secondi a queste domande:

1. **Cosa fa?** Una frase chiara, senza marketing.
2. **Come si vede?** Screenshot o GIF animata in alto. Le GIF di demo sono lo strumento più efficace per un'app GUI.
3. **Come si installa?** Comando `pip install` + link agli installer della release.
4. **Come si usa?** Esempi minimi.
5. **Come si contribuisce?** Link a `CONTRIBUTING.md`.
6. **Sotto quale licenza?** Badge.

Sezioni tipiche:

- Badge in testa: build status, versione PyPI, licenza, copertura test.
- Hero image / GIF.
- Features principali in elenco.
- Installazione (tre opzioni: installer, pip, da sorgente).
- Quickstart.
- Roadmap (link a `04-roadmap-mvp.md` o issue dedicate).
- Contributi.
- Licenza.

---

## 3. File di governance

### `CONTRIBUTING.md`

Spiega:

- Come configurare l'ambiente di sviluppo.
- Come eseguire test e linter.
- Lo stile di codice (rimanda a `ruff` e configurazioni in `pyproject.toml`).
- Il flusso di lavoro: fork → branch → PR.
- Convenzioni per i commit (es. [Conventional Commits](https://www.conventionalcommits.org/)).
- Cosa serve per far accettare una PR (test, descrizione, link a issue).

### `CODE_OF_CONDUCT.md`

Adottare il [Contributor Covenant](https://www.contributor-covenant.org/). È uno standard, basta copiarlo.

### `SECURITY.md`

Come segnalare vulnerabilità (email privata, **non** issue pubblica). Anche se il progetto è piccolo, averlo dimostra serietà.

### `CHANGELOG.md`

Formato consigliato: [Keep a Changelog](https://keepachangelog.com/). Categorie: Added, Changed, Deprecated, Removed, Fixed, Security.

### `AUTHORS.md` o `CONTRIBUTORS.md`

Elenco dei contributor. Si può generare automaticamente con [all-contributors](https://allcontributors.org/).

---

## 4. Template GitHub

Cartella `.github/`:

```
.github/
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml
│   ├── feature_request.yml
│   └── config.yml
├── PULL_REQUEST_TEMPLATE.md
├── FUNDING.yml             # se si vuole abilitare sponsor
└── workflows/
    ├── ci.yml
    ├── release.yml
    └── codeql.yml
```

I template **YAML** per le issue (form-based) sono molto più efficaci dei vecchi markdown perché obbligano l'utente a fornire le informazioni necessarie (versione, OS, passi per riprodurre).

---

## 5. Continuous Integration

Workflow `ci.yml` su GitHub Actions:

- Trigger: push e pull request su `main`.
- Matrix: Python 3.11/3.12/3.13 × Ubuntu/macOS/Windows.
- Step:
  1. Checkout.
  2. Setup Python.
  3. Install dipendenze.
  4. `ruff check` + `ruff format --check`.
  5. `mypy src/`.
  6. `pytest --cov`.
  7. Upload coverage (Codecov o simile).

Per la UI: `pytest-qt` con `xvfb` su Linux per i test headless.

---

## 6. Gestione delle issue

- **Labels** organizzate: `bug`, `feature`, `documentation`, `good first issue`, `help wanted`, `priority:high`, `area:ui`, `area:core`, `area:rendering`.
- **Milestones** allineate alle versioni della roadmap (v0.1, v0.2…).
- **Projects** (board Kanban) per visualizzare lo stato.
- Issue `good first issue` ben curate sono il modo numero uno per attrarre i primi contributor: piccole, ben descritte, con riferimenti al codice.
- Rispondere entro pochi giorni anche solo per ringraziare.

---

## 7. Branching e release

### Branching

Modello consigliato all'inizio: **trunk-based**.

- Un solo branch `main` sempre stabile.
- Feature branch corte, merge via PR con CI verde obbligatoria.
- Niente `develop` separato finché il progetto è piccolo.

### Versioning

[Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`.

- Pre-1.0: si parte da `0.1.0`. Le minor possono introdurre breaking changes (è la convenzione SemVer per lo "0.x").
- 1.0 quando l'API e l'esperienza utente sono stabili.

### Release

1. Aggiornare `CHANGELOG.md`.
2. Bumpare la versione in `pyproject.toml`.
3. Commit `chore: release v0.1.0`.
4. Tag `git tag v0.1.0 && git push --tags`.
5. Il workflow `release.yml` builda artefatti, crea la GitHub Release e pubblica su PyPI.

---

## 8. Comunicazione e community

Per un progetto agli inizi non serve un Discord. Bastano:

- **GitHub Discussions**: abilitarlo. Categorie: Q&A, Ideas, Show and tell, Announcements.
- **Issue tracker**: solo per bug e feature concrete.
- **Release notes**: scrivere bene quelle, anche brevi.

Più tardi, se la community cresce: Matrix/Discord, mailing list, blog.

---

## 9. Documentazione

Per il codice: docstring in stile Google o NumPy, controllate da `ruff`/`pydocstyle`.

Per gli utenti: documentazione separata generata con [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) o [Sphinx](https://www.sphinx-doc.org/). MkDocs è più semplice e moderno per progetti nuovi.

Pubblicare su **GitHub Pages** automaticamente da CI a ogni push su `main`.

Sezioni minime: Installazione, Primi passi, Guida utente, FAQ, Architettura (per contributor), API reference.

---

## 10. Sostenibilità

Aspetti spesso trascurati ma importanti:

- **Sponsor**: abilitare GitHub Sponsors o Open Collective. Anche cifre piccole danno motivazione.
- **Bus factor**: evitare che tutto dipenda da una sola persona. Documentare scelte e processi.
- **Burnout**: rispondere "no" o "non ora" è legittimo. Non è obbligatorio accettare ogni feature request.
- **Trademark**: se il nome del progetto diventa importante, considerare la registrazione.

---

## 11. Checklist iniziale per il primo commit pubblico

- [ ] `LICENSE` (AGPL-3.0).
- [ ] `README.md` con descrizione, screenshot (anche placeholder), installazione, uso base.
- [ ] `CONTRIBUTING.md`.
- [ ] `CODE_OF_CONDUCT.md`.
- [ ] `CHANGELOG.md` con sezione "Unreleased".
- [ ] `.gitignore` per Python.
- [ ] `pyproject.toml` configurato.
- [ ] `.github/workflows/ci.yml` funzionante.
- [ ] Issue templates.
- [ ] PR template.
- [ ] Almeno 3-5 issue `good first issue` aperte.
- [ ] GitHub Discussions abilitato.
- [ ] Topics del repository impostati (`pdf`, `pdf-editor`, `python`, `pyside6`, `pymupdf`).
- [ ] Description e website del repository compilati.

---

## 12. Errori comuni da evitare

- **Annunciare prima di avere qualcosa di funzionante.** L'hype senza demo brucia attenzione.
- **README troppo aspirazionale.** Descrivere ciò che il progetto fa **oggi**, non ciò che farà.
- **Accettare tutte le PR.** Meglio rifiutare con gentilezza che incorporare codice che non si vuole mantenere.
- **Ignorare le issue per settimane.** Anche un "grazie, lo guarderò più avanti" è meglio del silenzio.
- **Cambiare licenza dopo che ci sono contributor esterni.** Diventa quasi impossibile (servirebbe il consenso di tutti).
- **Non avere test.** Un progetto senza CI verde scoraggia i contributor.
