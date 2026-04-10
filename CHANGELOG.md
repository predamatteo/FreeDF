# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Initial project structure and build configuration
- Core PDF document model wrapping PyMuPDF
- Command pattern with undo/redo support (CommandStack)
- Page commands: rotate, delete, duplicate
- Page rendering with LRU cache
- PDF loading and saving (incremental + full)
- PySide6-based minimal GUI with page viewer and thumbnail sidebar
- Keyboard shortcuts for all operations
- Drag-and-drop PDF file opening
- CI pipeline (GitHub Actions) with lint, type check, and tests
