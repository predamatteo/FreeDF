# FreeDF

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![CI](https://img.shields.io/github/actions/workflow/status/FreeDF/FreeDF/ci.yml?branch=main&label=CI)](https://github.com/FreeDF/FreeDF/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)

> A free, open-source PDF editor. View, annotate, and manipulate PDF pages.

<!-- TODO: Add screenshot after first working version -->

## Features (v0.1)

- View and navigate PDF documents
- Zoom (in, out, fit width, fit page, 100%)
- Page thumbnails sidebar
- Rotate, delete, and duplicate pages
- Undo / redo for all operations
- Save and Save As
- Keyboard-driven workflow
- Drag-and-drop file opening

## Installation

### From PyPI

```bash
pip install freedf
freedf
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

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, coding standards, and PR guidelines.

## License

This project is licensed under the **GNU Affero General Public License v3.0** (AGPL-3.0).

This means you are free to use, modify, and distribute FreeDF, provided that:
- Any modified version you distribute or deploy (including as a network service) must also be released under AGPL-3.0.
- You must make the complete source code available to users.

See [LICENSE](LICENSE) for the full text.
