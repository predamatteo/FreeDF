# 05 — Distribuzione

Distribuire un'app Python come eseguibile è fattibile ma ha le sue insidie. Per un progetto open source su GitHub conviene supportare due canali paralleli: **PyPI** per chi ha già Python, **eseguibili standalone** per gli utenti finali.

## Canale 1 — PyPI

Per chi ha Python installato:

```bash
pip install pdf-editor
pdf-editor
```

Setup:

- `pyproject.toml` con `hatchling` come build backend.
- Definire un `entry_point` per il comando `pdf-editor` che lancia `pdfeditor.app:main`.
- Pubblicazione automatica su PyPI da GitHub Actions al tag di una nuova release (usando `pypa/gh-action-pypi-publish` con OIDC trusted publishing, niente token da gestire).

Esempio di `[project.scripts]` in `pyproject.toml`:

```toml
[project.scripts]
pdf-editor = "pdfeditor.app:main"
```

## Canale 2 — Eseguibili standalone

Per utenti finali senza Python.

### Opzioni

| Tool | Pro | Contro |
|---|---|---|
| **PyInstaller** | Standard de facto, flessibile, tantissima documentazione. | Bundle grandi (50-150 MB), falsi positivi antivirus su Windows. |
| **Briefcase** (BeeWare) | Produce installer nativi (.msi, .dmg, .deb, .AppImage). Più "pulito" per app GUI. | Meno diffuso, comunità più piccola. |
| **Nuitka** | Compila in C, output più veloce. | Build lente, qualche libreria fa i capricci. |

**Raccomandazione**: iniziare con **Briefcase** perché produce installer nativi puliti e gestisce bene PySide6. Tenere PyInstaller come piano B.

### Cosa includere nel bundle

- L'eseguibile Python embedded.
- Tutte le dipendenze (PyMuPDF, pikepdf, PySide6, Pillow…).
- Le librerie native incluse nei wheel di PyMuPDF e pikepdf (MuPDF e QPDF compilati).
- Risorse: icone, traduzioni, eventuali file di esempio.

I wheel pre-compilati di PyMuPDF e pikepdf sono disponibili per Windows/macOS/Linux su x86_64 e ARM64, quindi non serve compilare nulla manualmente.

## Code signing

Senza firma, gli utenti vedranno warning spaventosi all'apertura dell'installer.

### Windows
- Certificato code signing (Sectigo, DigiCert, ecc.) — circa 200-400€/anno.
- In alternativa, accettare i warning di SmartScreen (peggio per l'esperienza utente).
- Tool: `signtool.exe`.

### macOS
- **Apple Developer Program**: 99 USD/anno.
- Firma con Developer ID Application.
- **Notarization** obbligatoria per Gatekeeper.
- Tool: `codesign` + `notarytool`.
- Senza notarization l'utente deve fare clic destro → Apri.

### Linux
- Nessuna firma "standard". Se si distribuisce su Flathub o Snap Store, le piattaforme gestiscono la verifica.
- AppImage non richiede firma ma può essere firmato con GPG.

Per un progetto open source agli inizi, è ragionevole **iniziare senza certificati a pagamento** e documentare nel README come bypassare i warning. Aggiungere code signing quando il progetto avrà donatori o sponsor.

## Architetture

### macOS
Buildare separatamente per Intel e Apple Silicon, oppure produrre un **universal binary**. Briefcase gestisce questo.

### Linux
Distribuire come AppImage (portabile), Flatpak (sandbox, store), e/o Snap. AppImage è il più semplice per iniziare.

### Windows
x86_64 sufficiente all'inizio. ARM64 più avanti se nasce richiesta.

## Aggiornamenti automatici

Opzioni per il futuro:

- **Sparkle** su macOS (richiede integrazione nativa).
- **WinSparkle** su Windows.
- Soluzione custom: l'app controlla l'API GitHub Releases all'avvio e notifica nuove versioni, lasciando all'utente lo scaricamento.

La soluzione custom basata su GitHub Releases è la più semplice da implementare e non richiede infrastruttura.

## Release automatizzate da GitHub Actions

Workflow tipico, attivato al push di un tag `v*`:

1. Job per Linux: build wheel + AppImage.
2. Job per macOS: build .dmg firmato e notarizzato (se i secret sono configurati).
3. Job per Windows: build .msi firmato (se i secret sono configurati).
4. Job finale: crea una GitHub Release e allega tutti gli artefatti.
5. Job parallelo: pubblica il wheel su PyPI.

Esistono action già pronte come `softprops/action-gh-release` per la creazione della release.

## Checklist pre-release

- [ ] Tutti i test passano su tutte le piattaforme.
- [ ] CHANGELOG aggiornato.
- [ ] Versione bumpata in `pyproject.toml`.
- [ ] README e screenshot aggiornati se la UI è cambiata.
- [ ] Tag git creato e pushato.
- [ ] Release notes scritte.
- [ ] Verifica manuale degli installer su almeno una macchina per piattaforma.
