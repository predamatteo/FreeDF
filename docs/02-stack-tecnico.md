# 02 — Stack tecnico

Il progetto sarà rilasciato come **open source su GitHub**, presumibilmente sotto **AGPL-3.0**. Questa scelta sblocca le librerie copyleft più potenti dell'ecosistema Python.

## Licenza del progetto

**AGPL-3.0** è la scelta consigliata perché:

- È compatibile con PyMuPDF (AGPL), che è di gran lunga la libreria PDF Python più completa.
- Copre anche l'uso "as a service" (chi offre il software via web deve rilasciare il codice).
- Mantiene il progetto genuinamente libero e protegge da appropriazioni commerciali chiuse.

Alternative: GPL-3.0 (non copre SaaS), MIT/Apache (non permettono PyMuPDF senza licenza commerciale Artifex).

## Librerie PDF

### PyMuPDF (`pymupdf`, importata come `fitz`) — motore principale

Binding di MuPDF. Copre da sola gran parte del lavoro:

- Rendering ad alta qualità delle pagine in immagini.
- Estrazione testo con coordinate (blocchi, righe, caratteri).
- Annotazioni: creazione, modifica, eliminazione (highlight, ink, freetext, stamp, link…).
- Inserimento e modifica di immagini.
- Manipolazione pagine: merge, split, rotazione, riordino.
- Compilazione form AcroForm.
- OCR integrato (richiede Tesseract installato).

### pikepdf — utility a basso livello

Da tenere nel toolkit per i casi in cui serve scendere al livello degli oggetti PDF grezzi: modificare strutture che PyMuPDF non espone direttamente, "PDF surgery", riparazioni. Le due librerie coesistono bene.

### Pillow

Manipolazione immagini. PyMuPDF restituisce pixmap convertibili in `PIL.Image`.

### pytesseract (opzionale)

Se servirà un controllo più fine sull'OCR rispetto al wrapper integrato di PyMuPDF.

## GUI: PySide6

**PySide6** (binding Qt ufficiale, LGPL) è la scelta consigliata.

Motivi:

- Maturo e ben documentato.
- Compatibile con AGPL.
- `QGraphicsView` / `QGraphicsScene` è ideale per un editor: si renderizza la pagina come `QGraphicsPixmapItem` e sopra si aggiungono `QGraphicsItem` custom per annotazioni, selezioni, handle di resize.
- Ottima gestione di eventi mouse/tastiera, zoom, panning.
- Build cross-platform (Windows, macOS, Linux).

Alternative considerate e scartate:

- **PyQt6**: stesso Qt, GPL/commerciale. Compatibile con AGPL ma PySide6 è quello ufficiale.
- **Tkinter**: troppo limitato per un editor serio.
- **wxPython**: valido ma meno moderno.
- **Toga / BeeWare**: promettente ma meno maturo.

## Riepilogo dello stack

| Componente | Libreria | Licenza |
|---|---|---|
| Motore PDF | PyMuPDF | AGPL-3.0 |
| PDF a basso livello | pikepdf | MPL-2.0 |
| Immagini | Pillow | HPND |
| GUI | PySide6 | LGPL-3.0 |
| OCR (opzionale) | pytesseract + Tesseract | Apache-2.0 / Apache-2.0 |
| Test | pytest | MIT |
| Lint/format | ruff | MIT |
| Type check | mypy | MIT |
| Packaging | hatchling + briefcase/pyinstaller | MIT |
