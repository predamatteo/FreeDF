# FreeDF

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![CI](https://img.shields.io/github/actions/workflow/status/FreeDF/FreeDF/ci.yml?branch=main&label=CI)](https://github.com/FreeDF/FreeDF/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.5.0-brightgreen)](https://github.com/FreeDF/FreeDF/releases)

> A free, open-source PDF editor. View, annotate, manipulate, and OCR PDF documents.

<!-- TODO: Add screenshot or demo GIF -->

## Features

### Viewing & Navigation
- Open, view, and navigate PDF documents
- Zoom (in, out, fit width, fit page)
- Page thumbnail sidebar with drag-and-drop reordering
- Drag-and-drop file opening

### Annotations
- Highlight text selection
- FreeText notes
- Freehand ink drawing
- Shapes: rectangle, ellipse, line, arrow
- Select, move, and delete annotations
- Configurable colors and line thickness
- Annotation list sidebar

### Page Operations
- Rotate, delete, duplicate, reorder pages
- Merge multiple PDFs
- Split PDF by page ranges or single pages
- Extract selected pages to a new file
- Insert pages from another PDF

### Forms & Images
- Detect and fill AcroForm fields
- Insert images/signatures on pages
- Flatten annotations into page content

### OCR & Text
- OCR scanned pages via Tesseract
- Text selection and copy
- Export text to file or clipboard

### Editing
- Full undo/redo for all operations
- Recent files menu
- Keyboard-driven workflow

## Installation

### From PyPI

```bash
pip install freedf
freedf
```

With OCR support:
```bash
pip install freedf[ocr]
```

### From source

```bash
git clone https://github.com/FreeDF/FreeDF.git
cd FreeDF
pip install -e ".[dev]"
freedf
```

## Usage

```bash
freedf                    # launch empty
freedf document.pdf       # open a file
```

## Roadmap

Completed: v0.1 (viewing, page ops, basic annotations), v0.2 (annotation expansion), v0.3 (multi-file ops), v0.4 (forms & images), v0.5 (OCR & text).

Planned:
- Dark theme
- UI internationalization (i18n)
- Headless CLI for batch operations
- Plugin system
- Digital signatures
- PDF comparison

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

## License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).
See [LICENSE](LICENSE) for the full text.
