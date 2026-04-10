# 04 — Roadmap e MVP

## Filosofia

Partire da un MVP molto ristretto che però **chiuda il ciclo completo**: aprire → renderizzare → modificare → salvare. Quando questo ciclo funziona, si ha già il 70% dell'architettura, e tutto il resto è incrementale.

## v0.1 — MVP "pubblicabile"

Set minimo di funzionalità per un primo rilascio su GitHub che abbia già senso usare:

### Visualizzazione
- [ ] Apertura PDF (drag & drop + dialog).
- [ ] Visualizzazione pagina con `QGraphicsView`.
- [ ] Zoom (in, out, fit width, fit page, 100%).
- [ ] Navigazione tra pagine (frecce, page up/down, vai a pagina).
- [ ] Sidebar con miniature delle pagine.

### Manipolazione pagine
- [ ] Ruotare pagina (90° / 180° / 270°).
- [ ] Eliminare pagina.
- [ ] Duplicare pagina.
- [ ] Riordinare pagine (drag & drop nella sidebar miniature).

### Annotazioni base
- [ ] Highlight su testo selezionato.
- [ ] Nota testuale libera (freetext annotation).

### File
- [ ] Salva.
- [ ] Salva con nome.
- [ ] File recenti.

### Editing
- [ ] Undo / redo (Ctrl+Z / Ctrl+Shift+Z) basato su CommandStack.

### Qualità
- [ ] Test del core e dei commands.
- [ ] CI su Linux/macOS/Windows.
- [ ] README con screenshot.
- [ ] Build standalone almeno per una piattaforma.

## v0.2 — Espansione annotazioni

- [ ] Disegno a mano libera (ink annotation).
- [ ] Forme: rettangolo, ellisse, freccia, linea.
- [ ] Selezione, spostamento, eliminazione, modifica colore di annotazioni esistenti.
- [ ] Colori e spessori configurabili.
- [ ] Pannello laterale con elenco annotazioni della pagina.

## v0.3 — Operazioni multi-file

- [ ] Merge di più PDF.
- [ ] Split di un PDF in più file.
- [ ] Estrai pagine in un nuovo PDF.
- [ ] Inserisci pagine da un altro PDF.

## v0.4 — Form e firme

- [ ] Compilazione campi AcroForm.
- [ ] Inserimento immagine/firma raster su pagina.
- [ ] Esportazione "flatten" delle annotazioni nel contenuto.

## v0.5 — OCR e accessibilità

- [ ] OCR di pagine scansionate (Tesseract).
- [ ] Selezione testo dopo OCR.
- [ ] Esportazione testo estratto.

## Backlog / future

- Editing del contenuto testuale (con tutte le difficoltà del caso sui font).
- Firma digitale.
- Confronto tra due PDF.
- Plugin system.
- Internazionalizzazione UI.
- Tema scuro.
- Versione headless / CLI.

## Criteri "definition of done" per ogni feature

1. La logica è in `core/` o `commands/`, senza dipendenze da Qt.
2. Esiste un test automatico che la copre.
3. È accessibile da menu, toolbar e (dove sensato) shortcut tastiera.
4. Funziona con undo/redo.
5. È documentata nel README o nei docs.
