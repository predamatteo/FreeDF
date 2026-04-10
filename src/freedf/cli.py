"""FreeDF headless CLI — batch PDF operations without GUI.

This module must NOT import Qt/PySide6.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="freedf-cli",
        description="FreeDF command-line PDF tools",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # merge
    p_merge = subparsers.add_parser("merge", help="Merge multiple PDFs")
    p_merge.add_argument("files", nargs="+", help="PDF files to merge")
    p_merge.add_argument("-o", "--output", required=True, help="Output file")

    # split
    p_split = subparsers.add_parser("split", help="Split a PDF")
    p_split.add_argument("file", help="Input PDF")
    p_split.add_argument("-o", "--output", required=True, help="Output directory")
    p_split.add_argument(
        "--pages",
        help="Page range (e.g., '1-3' or 'all' for single pages)",
        default="all",
    )

    # extract
    p_extract = subparsers.add_parser("extract", help="Extract pages")
    p_extract.add_argument("file", help="Input PDF")
    p_extract.add_argument(
        "--pages", required=True, help="Pages to extract (e.g., '1,3,5')"
    )
    p_extract.add_argument("-o", "--output", required=True, help="Output file")

    # rotate
    p_rotate = subparsers.add_parser("rotate", help="Rotate pages")
    p_rotate.add_argument("file", help="Input PDF")
    p_rotate.add_argument(
        "--page", type=int, required=True, help="Page number (1-based)"
    )
    p_rotate.add_argument(
        "--degrees", type=int, required=True, choices=[90, 180, 270], help="Rotation"
    )
    p_rotate.add_argument("-o", "--output", required=True, help="Output file")

    # text
    p_text = subparsers.add_parser("text", help="Extract text")
    p_text.add_argument("file", help="Input PDF")
    p_text.add_argument("-o", "--output", help="Output .txt file (default: stdout)")

    # info
    p_info = subparsers.add_parser("info", help="Show PDF info")
    p_info.add_argument("file", help="Input PDF")

    # ocr
    p_ocr = subparsers.add_parser("ocr", help="OCR scanned pages")
    p_ocr.add_argument("file", help="Input PDF")
    p_ocr.add_argument("-o", "--output", required=True, help="Output PDF")
    p_ocr.add_argument("--lang", default="eng", help="OCR language (default: eng)")
    p_ocr.add_argument("--dpi", type=int, default=300, help="Render DPI (default: 300)")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    try:
        _dispatch(args)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


def _dispatch(args: argparse.Namespace) -> None:
    cmd = args.command
    if cmd == "merge":
        _cmd_merge(args)
    elif cmd == "split":
        _cmd_split(args)
    elif cmd == "extract":
        _cmd_extract(args)
    elif cmd == "rotate":
        _cmd_rotate(args)
    elif cmd == "text":
        _cmd_text(args)
    elif cmd == "info":
        _cmd_info(args)
    elif cmd == "ocr":
        _cmd_ocr(args)


def _cmd_merge(args: argparse.Namespace) -> None:
    from freedf.core.multifile import merge_pdfs

    merge_pdfs(args.files, args.output)
    print(f"Merged {len(args.files)} files -> {args.output}")


def _cmd_split(args: argparse.Namespace) -> None:
    from freedf.core.multifile import split_pdf_by_ranges, split_pdf_single_pages

    if args.pages == "all":
        results = split_pdf_single_pages(args.file, args.output)
    else:
        parts = args.pages.split("-")
        start, end = int(parts[0]) - 1, int(parts[1]) - 1
        results = split_pdf_by_ranges(args.file, [(start, end)], args.output)
    print(f"Created {len(results)} files in {args.output}")


def _cmd_extract(args: argparse.Namespace) -> None:
    from freedf.core.multifile import extract_pages

    page_nums = [int(p.strip()) - 1 for p in args.pages.split(",")]
    extract_pages(args.file, page_nums, args.output)
    print(f"Extracted {len(page_nums)} pages -> {args.output}")


def _cmd_rotate(args: argparse.Namespace) -> None:
    import shutil

    from freedf.io.loader import open_pdf
    from freedf.io.saver import save_as

    shutil.copy(args.file, args.output)
    doc = open_pdf(args.output)
    doc.rotate_page(args.page - 1, args.degrees)
    save_as(doc, args.output)
    doc.close()
    print(f"Rotated page {args.page} by {args.degrees} degrees -> {args.output}")


def _cmd_text(args: argparse.Namespace) -> None:
    from freedf.core.text_export import extract_text_from_document
    from freedf.io.loader import open_pdf

    doc = open_pdf(args.file)
    text = extract_text_from_document(doc)
    doc.close()
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Text exported -> {args.output}")
    else:
        print(text)


def _cmd_info(args: argparse.Namespace) -> None:
    from freedf.core.forms import detect_form_fields
    from freedf.io.loader import open_pdf

    doc = open_pdf(args.file)
    meta = doc.metadata
    print(f"File: {args.file}")
    print(f"Pages: {doc.page_count}")
    for key, value in meta.items():
        if value:
            print(f"{key}: {value}")
    fields = detect_form_fields(doc)
    if fields:
        print(f"\nForm fields ({len(fields)}):")
        for f in fields:
            print(f"  - {f.field_name} ({f.field_type}): {f.current_value!r}")
    doc.close()


def _cmd_ocr(args: argparse.Namespace) -> None:
    import shutil

    from freedf.core.ocr import (
        apply_ocr_text_layer,
        is_tesseract_available,
        ocr_page,
        page_has_text,
    )
    from freedf.io.loader import open_pdf
    from freedf.io.saver import save_as

    if not is_tesseract_available():
        print("Error: Tesseract is not installed", file=sys.stderr)
        sys.exit(1)

    shutil.copy(args.file, args.output)
    doc = open_pdf(args.output)
    count = 0
    for i in range(doc.page_count):
        if not page_has_text(doc, i):
            print(f"  OCR page {i + 1}...")
            result = ocr_page(doc, i, language=args.lang, dpi=args.dpi)
            apply_ocr_text_layer(doc, i, result)
            count += 1
    save_as(doc, args.output)
    doc.close()
    print(f"OCR completed: {count} pages processed -> {args.output}")


if __name__ == "__main__":
    main()
