# 03 — Architettura

## Principio guida

Tre livelli nettamente separati. **Il livello `core/` non importa mai Qt.**

Questo permette di:

- Testare tutto in CI senza display.
- Scrivere in futuro una CLI o una versione headless.
- Mantenere un confine architetturale chiaro.
- Facilitare contributi esterni (più facile orientarsi).

## Struttura del repository

```
pdf-editor/
├── src/
│   └── pdfeditor/
│       ├── __init__.py
│       ├── core/           # Modello PDF, operazioni pure (no Qt)
│       │   ├── document.py        # Wrapper PyMuPDF/pikepdf
│       │   ├── page.py
│       │   ├── annotations.py
│       │   └── exceptions.py
│       ├── commands/       # Pattern Command per undo/redo (no Qt)
│       │   ├── base.py            # Command + CommandStack
│       │   ├── page_commands.py   # Rotate, Delete, Reorder, Duplicate
│       │   └── annotation_commands.py
│       ├── rendering/      # Renderer + cache (no Qt)
│       │   ├── renderer.py
│       │   └── cache.py
│       ├── io/             # Apertura, salvataggio, recenti, autosave
│       │   ├── loader.py
│       │   └── saver.py
│       ├── ui/             # Tutto il codice Qt
│       │   ├── main_window.py
│       │   ├── page_view.py       # QGraphicsView custom
│       │   ├── page_scene.py      # QGraphicsScene
│       │   ├── thumbnails.py      # Sidebar miniature
│       │   ├── tools/             # Strumenti di editing (highlight, nota...)
│       │   └── dialogs/
│       └── app.py          # Entry point
├── tests/
│   ├── test_core/
│   ├── test_commands/
│   ├── test_rendering/
│   └── fixtures/           # PDF di esempio per i test
├── docs/
├── pyproject.toml
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
└── .github/
    ├── workflows/
    └── ISSUE_TEMPLATE/
```

## I tre livelli

### 1. Core (modello)

Wrapping di PyMuPDF/pikepdf. Espone pagine, oggetti, metadati, annotazioni. **Tutte le modifiche al PDF passano da qui.**

Regola: nessun import di Qt, nessuna dipendenza dalla UI. Deve poter essere usato da uno script standalone.

### 2. Renderer

Prende un riferimento a una pagina e una scala/DPI, restituisce un'immagine (es. `bytes` PNG o `PIL.Image`).

- Cache LRU delle pagine renderizzate per (page_number, zoom_level).
- Rendering asincrono opzionale per non bloccare la UI.
- Nessun import di Qt: la UI converte il risultato in `QPixmap`.

### 3. UI

`QGraphicsScene` mostra la pagina renderizzata come `QGraphicsPixmapItem`. Sopra si sovrappongono `QGraphicsItem` custom per annotazioni e selezioni. Quando l'utente conferma una modifica, viene creato un **Command** che agisce sul Core.

## Pattern Command per undo/redo

Ogni operazione di editing è un oggetto con due metodi:

```python
class Command(Protocol):
    def execute(self) -> None: ...
    def undo(self) -> None: ...
```

Esempi: `AddHighlightCommand`, `DeletePageCommand`, `RotatePageCommand`, `ReorderPagesCommand`.

Uno `CommandStack` mantiene la pila di comandi eseguiti e quella di redo. Vantaggi:

- Undo/redo gratis e robusto.
- Test unitari sui comandi senza UI.
- Possibilità futura di registrare macro o batch operations.
- Log delle operazioni utente per debugging.

## Flusso tipico di un'operazione

1. L'utente interagisce con la UI (es. seleziona testo e clicca "Highlight").
2. La UI raccoglie i parametri (pagina, rettangoli, colore).
3. La UI crea un `AddHighlightCommand(document, page_num, rects, color)`.
4. Il `CommandStack` esegue il comando, che modifica il modello Core.
5. La UI riceve un segnale "pagina modificata" e invalida la cache di rendering per quella pagina.
6. La pagina viene ri-renderizzata e mostrata.

## Test

- **Core e commands**: testabili senza Qt. Usare PDF di fixture in `tests/fixtures/`.
- **Rendering**: test che verificano dimensioni, hash dell'immagine, performance.
- **UI**: test minimi con `pytest-qt` per gli smoke test delle finestre principali.

Obiettivo realistico: copertura alta su core e commands, copertura best-effort sulla UI.
