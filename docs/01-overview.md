# 01 — Overview: capire il problema

## Cos'è davvero un PDF

Un PDF non è un documento "modificabile" come un file Word: è essenzialmente una **descrizione di come disegnare delle pagine**. Ogni pagina contiene un *content stream* con istruzioni grafiche del tipo "posiziona questo glifo a queste coordinate, traccia questa linea là".

Conseguenze pratiche:

- Il testo non è organizzato in paragrafi o righe logiche, ma in singoli pezzi posizionati a coordinate assolute.
- "Modificare una parola" non è banale: bisogna trovare il glifo giusto, sostituirlo, e potenzialmente ricalcolare il layout.
- L'ordine di lettura del testo estratto può non corrispondere all'ordine visivo.
- I font sono spesso embeddati come *subset*: contengono solo i caratteri effettivamente usati nel documento.

## Specifica di riferimento

- **ISO 32000-1** (PDF 1.7) — la versione più diffusa.
- **ISO 32000-2** (PDF 2.0) — più recente, meno supportata.

Non serve leggerla tutta. I capitoli utili sono: struttura del file, oggetti, content stream, font, annotazioni.

## Livelli di "editing" possibili

Editor PDF può voler dire cose molto diverse. Conviene scegliere uno scope ristretto all'inizio.

| Livello | Cosa significa | Difficoltà |
|---|---|---|
| Annotazioni | Highlight, note, frecce, firme. Oggetti separati dal contenuto. | Bassa |
| Manipolazione pagine | Unire, dividere, ruotare, riordinare, estrarre. | Bassa |
| Compilazione form | Leggere e scrivere campi AcroForm. | Media |
| Editing contenuto | Modificare testo e immagini esistenti. | Alta (font, reflow) |
| Editing strutturale | Tagged PDF, accessibilità. | Alta |

## Problemi che faranno tribolare

- **Font**: subset, encoding custom, glifi mancanti se aggiungi caratteri nuovi.
- **Estrazione testo**: ordine di lettura non garantito.
- **PDF scansionati**: sono immagini, serve OCR (Tesseract).
- **Firme digitali**: si invalidano se modifichi il file.
- **PDF criptati, PDF/A, form XFA**: casi speciali da gestire.
- **File mal formati**: le librerie devono essere "permissive".

## Decisione di scope per questo progetto

Il progetto si concentrerà inizialmente su:

1. Visualizzazione e navigazione.
2. Manipolazione di pagine (riordina, ruota, elimina, duplica).
3. Annotazioni base (highlight, nota testuale).
4. Salvataggio e undo/redo.

L'editing del contenuto testuale è esplicitamente **fuori scope** per il primo rilascio.
