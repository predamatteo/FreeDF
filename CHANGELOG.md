# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Dark theme with toggle in View menu
- Internationalization (English + Italian)
- Headless CLI (`freedf-cli`) for merge, split, extract, rotate, OCR, text export
- Plugin system with entry point discovery

## [0.5.0] - 2026-04-10

### Added

- OCR support via Tesseract (optional: `pip install freedf[ocr]`)
- OCR dialog with language, DPI, and scope selection
- Text extraction and export (to file or clipboard)
- Text selection tool with copy support
- Export text dialog with page range and preview

## [0.4.0] - 2026-04-10

### Added

- AcroForm field detection and filling with FormPanel sidebar
- Image/signature insertion on pages with dialog
- Flatten annotations command (bakes annotations into page content)
- Fill field command with undo/redo

## [0.3.0] - 2026-04-10

### Added

- Merge multiple PDFs into one
- Split PDF by page ranges or single pages
- Extract selected pages to a new PDF
- Insert pages from another PDF (undoable)
- Merge, split, extract, and insert dialogs
- WorkerThread base class for long-running operations

## [0.2.0] - 2026-04-10

### Added

- Ink (freehand drawing) annotation tool with live preview
- Shape annotations: rectangle, ellipse, line, arrow
- Annotation selection, move, and delete via select tool
- Color picker and thickness picker widgets in toolbar
- Annotation list sidebar panel
- Modify annotation command for undo/redo

## [0.1.0] - 2026-04-10

### Added

- Initial project structure with AGPL-3.0 license
- PDF viewing with QGraphicsView (zoom, pan, scroll)
- Page navigation (arrows, page up/down, first/last)
- Page thumbnail sidebar
- Page operations: rotate, delete, duplicate, reorder (drag-and-drop)
- Highlight annotation on selected text
- FreeText annotation with input dialog
- Save and Save As (incremental + full rewrite)
- Undo/redo for all operations via CommandStack
- Recent files menu with JSON persistence
- Drag-and-drop file opening
- Minimal UI theme (white/gray/green accent)
- CI pipeline (GitHub Actions) with ruff, mypy, pytest
- File menu with Open, Save, Save As, Recent, Quit
