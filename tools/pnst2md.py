#!/usr/bin/env python3
# -----------------------------------------------------------------------------
# The CyberiadaML-GraphML standard compatibility tests
#
# Layout-aware PDF to Markdown converter for the PNST standard documents
#
# Copyright (C) 2026 Alexey Fedoseev <aleksey@fedoseev.net>
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see https://www.gnu.org/licenses/
#
# -----------------------------------------------------------------------------

"""Convert a PNST standard PDF into Markdown.

    python3 tools/pnst2md.py IN.pdf OUT.md IMAGEDIR

The converter reconstructs what plain text extraction loses: blank lines
inside listings (from the line pitch), code blocks (from the Courier
font), headings (from the bold font and clause numbering) and the real
figures (embedded images that are not part of the repeating page
watermark). The output is a faithful mirror of the document text.
"""

import pathlib
import re
import sys

import pypdf

try:
    import pymupdf
except ImportError:          # figures are skipped without pymupdf
    pymupdf = None

CODE_FONT = "Courier"
BOLD_FONT = "Bold"
BULLETS = "•●−"
SYMBOL_FONTS = ("OpenSymbol",)
HEADING = re.compile(r"^(\d+(?:\.\d+)*)\s*(?=[А-ЯA-Z(«])")
APPENDIX = re.compile(r"^Приложение\s+[А-Я]\b")
APP_SUB = re.compile(r"^([А-Я])\.(\d+(?:\.\d+)*)\s*(?=[А-ЯA-Z(«])")
TABLE_CAPTION = re.compile(r"^Т а б л и ц а\s*(\d+)\s*[–—-]?\s*(.*)$")
NOTE_CELL = re.compile(r"^П\s?р\s?и\s?м\s?е\s?ч\s?а\s?н\s?и\s?[ея]")
TOC_LINE = re.compile(r"\.{4,}\s*\d*\s*$")
PAGE_NUMBER = re.compile(r"^(\d{1,3}|[IVX]{1,4})$")
FIGURE = re.compile(r"^Рисунок\s+[\w.]+\s*[—–-]")
FRONT_HEADINGS = ("Предисловие", "Введение", "Содержание",
                  "Библиография")


class Line:
    def __init__(self, y):
        self.y = y
        self.chunks = []          # (x, text, font, size)

    def text(self):
        chunks = sorted(self.chunks, key=lambda c: c[0])
        parts = []
        previous = None
        for x, chunk, font, size in chunks:
            if previous is not None:
                p_chunk, p_font, p_x, p_size = previous
                if CODE_FONT in (font or "") and p_font == font:
                    # monospace: reconstruct spaces from the x gap
                    width = (p_size or 10) * 0.6
                    gap = x - (p_x + len(p_chunk) * width)
                    if gap > width * 0.5:
                        parts.append(" " * max(1, round(gap / width)))
                elif font != p_font and p_chunk and chunk and \
                        p_chunk[-1].isalnum() and chunk[0].isalnum():
                    parts.append(" ")     # space lost at a font boundary
            parts.append(chunk)
            previous = (chunk, font, x, size)
        return "".join(parts)

    def bullet_text(self):
        """(is bullet, text without the leading symbol glyph)."""
        chunks = sorted(self.chunks, key=lambda c: c[0])
        first = chunks[0]
        if len(first[1].strip()) <= 2 and \
                any(s in (first[2] or "") for s in SYMBOL_FONTS):
            return True, "".join(t for _, t, _, _ in chunks[1:])
        return False, self.text()

    def font(self):
        best, size = "", 0
        for _, t, f, _ in self.chunks:
            if len(t.strip()) > size:
                best, size = f or "", len(t.strip())
        return best

    def x(self):
        return min(x for x, _, _, _ in self.chunks)


def page_lines(page):
    lines = {}

    def visitor(text, cm, tm, fd, fs):
        if not text.strip():
            return
        y = round(tm[5], 1)
        font = str(fd.get("/BaseFont", "")) if fd else ""
        lines.setdefault(y, Line(y)).chunks.append((tm[4], text, font, fs))
    page.extract_text(visitor_text=visitor)
    return [lines[y] for y in sorted(lines, reverse=True)]


def is_code(line):
    total = code = 0
    for _, chunk, font, _ in line.chunks:
        length = len(chunk.strip())
        total += length
        if CODE_FONT in (font or ""):
            code += length
    return total > 0 and code / total > 0.6


def is_furniture(text):
    stripped = text.strip()
    return stripped == "ПНСТ" or PAGE_NUMBER.match(stripped) or \
        re.match(r"^ПНСТ\s+1044", stripped)


def heading_level(text, font):
    stripped = text.strip()
    if stripped in FRONT_HEADINGS:
        return 2, stripped
    if APPENDIX.match(stripped):
        return 2, stripped
    sub = APP_SUB.match(stripped)
    if sub and BOLD_FONT in font and len(stripped) < 90:
        number = stripped[:sub.end()].strip()
        return min(number.count(".") + 2, 5), \
            number + " " + stripped[sub.end():].strip()
    match = HEADING.match(stripped)
    if match and BOLD_FONT in font and len(stripped) < 90:
        number = match.group(1)
        title = stripped[match.end():].strip()
        return min(len(number.split(".")) + 1, 5), number + " " + title
    return None, stripped


def normalize_body(text):
    stripped = text.strip()
    if stripped and stripped[0] in BULLETS:
        stripped = "- " + stripped[1:].strip()
    stripped = re.sub(r"^(\d{1,2})(?=[А-Я])", r"\1 ", stripped)
    stripped = re.sub(r"^\[(\d+)\](?=\S)", r"[\1] ", stripped)
    return re.sub(r"\s+", " ", stripped)


def code_pitch(gaps):
    steps = [g for g in gaps if 8 < g < 18]
    if not steps:
        return 12.4
    steps.sort()
    return steps[len(steps) // 2]


class Writer:
    def __init__(self):
        self.out = []
        self.mode = None          # None | "code" | "body"

    def open_code(self, xml):
        if self.mode != "code":
            self.close()
            self.out.append("```xml" if xml else "```")
            self.mode = "code"

    def close(self):
        if self.mode == "code":
            self.out.append("```")
            self.out.append("")
        elif self.mode == "body":
            self.out.append("")
        self.mode = None

    def code(self, text, blanks):
        self.out.extend([""] * blanks)
        self.out.append(text.rstrip())

    def body(self, text):
        if self.mode != "body":
            self.close()
            self.mode = "body"
        self.out.append(text)

    def heading(self, level, text):
        self.close()
        self.out.append("#" * level + " " + text)
        self.out.append("")

    def paragraph_break(self):
        if self.mode == "body":
            self.out.append("")
            self.mode = None


def render_figures(pdf_path, image_dir):
    """Render the figure regions to PNG files; return {page: [names]}.

    A figure occupies the band between the lowest wide body paragraph
    above its caption and the caption line itself; the band is rendered
    from the page, covering both raster and vector figures.
    """
    if pymupdf is None:
        print("pymupdf not available: figures skipped", file=sys.stderr)
        return {}
    doc = pymupdf.open(pdf_path)
    image_dir = pathlib.Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    by_page = {}
    index = 0
    for number in range(len(doc)):
        page = doc[number]
        for caption in page.search_for("Рисунок "):
            index += 1
            top = 45
            for block in page.get_text("blocks"):
                x0, y0, x1, y1, content = block[:5]
                if y1 <= caption.y0 - 4 and (x1 - x0) > 300 and \
                        len(content.strip()) > 40:
                    top = max(top, y1)
            region = pymupdf.Rect(40, top + 3, 570, caption.y0 - 1)
            name = "figure-%d.png" % index
            page.get_pixmap(clip=region, dpi=180).save(image_dir / name)
            by_page.setdefault(number + 1, []).append(name)
    return by_page


def _cell(text):
    text = (text or "").replace("|", "\\|").strip()
    return "<br>".join(part.strip() for part in text.split("\n"))


def collect_tables(pdf_path, image_dir):
    """Markdown tables per page: {page: [(top, bottom, kind, payload)]}.

    Coordinates are bottom-up (pypdf) y values. kind is "note" for the
    framed GOST notes and "table" otherwise; graphics-only cells are
    rendered to image files.
    """
    if pymupdf is None:
        return {}
    doc = pymupdf.open(pdf_path)
    image_dir = pathlib.Path(image_dir)
    image_dir.mkdir(parents=True, exist_ok=True)
    regions = {}
    for number in range(len(doc)):
        page = doc[number]
        height = page.rect.height
        for table in page.find_tables().tables:
            data = table.extract()
            box = pymupdf.Rect(table.bbox)
            top, bottom = height - box.y0, height - box.y1
            first = _cell(data[0][0]) if data and data[0] else ""
            if len(data) == 1 and NOTE_CELL.match(first):
                text = "Примечание " + " ".join(
                    _cell(c) for c in data[0][1:] if c)
                payload = re.sub(r"\s+", " ", text).strip()
                kind = "note"
            else:
                rows = []
                for r, row in enumerate(data):
                    cells = []
                    for c, cell in enumerate(row):
                        text = _cell(cell)
                        if not text:
                            rect = pymupdf.Rect(table.cells[
                                r * len(row) + c]) if False else None
                            try:
                                rect = pymupdf.Rect(
                                    table.rows[r].cells[c])
                            except Exception:
                                rect = None
                            if rect is not None and rect.height > 18 and \
                                    rect.width > 25:
                                name = "table-p%d-r%dc%d.png" % \
                                    (number + 1, r, c)
                                page.get_pixmap(
                                    clip=rect, dpi=150).save(
                                    image_dir / name)
                                text = "![](images/%s)" % name
                        cells.append(text)
                    rows.append(cells)
                payload = rows
                kind = "table"
            regions.setdefault(number + 1, []).append(
                [top, bottom, kind, payload, False])
    return regions


def table_markdown(rows):
    width = max(len(r) for r in rows)
    rows = [r + [""] * (width - len(r)) for r in rows]
    lines = ["| " + " | ".join(rows[0]) + " |",
             "|" + "---|" * width]
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def convert(pdf_path, md_path, image_dir):
    reader = pypdf.PdfReader(pdf_path)
    by_page = render_figures(pdf_path, image_dir)
    tables = collect_tables(pdf_path, image_dir)

    writer = Writer()
    writer.out.append("<!-- Generated from %s by tools/pnst2md.py; "
                      "the printed table of contents is omitted. -->" %
                      pathlib.Path(pdf_path).name)
    writer.out.append("")
    in_toc = False
    for number, page in enumerate(reader.pages, 1):
        lines = page_lines(page)
        pending_images = list(by_page.get(number, []))
        previous_y = None
        pitch_gaps = [b.y - a.y for a, b in zip(lines[1:], lines[:-1])]
        pitch = code_pitch(pitch_gaps)
        page_regions = tables.get(number, [])
        for line in lines:
            region = next((r for r in page_regions
                           if r[1] - 2 <= line.y <= r[0] + 2), None)
            if region is not None:
                if not region[4]:
                    region[4] = True
                    writer.close()
                    if region[2] == "note":
                        writer.body(region[3])
                        writer.paragraph_break()
                    else:
                        writer.out.extend(table_markdown(region[3]))
                        writer.out.append("")
                previous_y = None
                continue
            bullet, text = line.bullet_text()
            if is_furniture(text):
                continue
            if TOC_LINE.search(text):
                continue
            level, stripped = heading_level(text, line.font())
            if level is not None:
                if in_toc and APPENDIX.match(stripped):
                    continue          # wrapped table-of-contents entry
                in_toc = stripped == "Содержание"
                if not in_toc:
                    writer.heading(level, normalize_body(stripped))
                previous_y = None
                continue
            if in_toc:
                continue
            if text.strip() == "↳" and writer.mode == "code":
                writer.code("↳", 0)
                previous_y = line.y
                continue
            if is_code(line):
                blanks = 0
                if previous_y is not None:
                    blanks = max(0, round((previous_y - line.y) / pitch) - 1)
                writer.open_code(text.lstrip().startswith("<"))
                writer.code(text, blanks)
                previous_y = line.y
                continue
            previous_y = None
            body = normalize_body(text)
            caption = TABLE_CAPTION.match(body)
            if caption:
                writer.paragraph_break()
                body = "**Таблица %s – %s**" % (caption.group(1),
                                                caption.group(2))
                writer.body(body)
                writer.paragraph_break()
                continue
            if bullet:
                body = "- " + body
            if not body:
                continue
            if FIGURE.match(body):
                writer.close()
                if pending_images:
                    writer.out.append("![%s](images/%s)" %
                                      (body, pending_images.pop(0)))
                    writer.out.append("")
                writer.body(body)
                writer.paragraph_break()
                continue
            x = line.x()
            if body.startswith("- "):
                writer.paragraph_break()
            elif re.match(r"^-\S", body) and x > 130:
                body = "  - " + body[1:]      # nested value list
            elif 66 < x < 95:
                writer.paragraph_break()      # indented paragraph start
            writer.body(body)
    writer.close()
    text = "\n".join(writer.out).rstrip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    pathlib.Path(md_path).write_text(text, encoding="utf-8")
    print("written %s (%d lines), %d figures" %
          (md_path, text.count("\n"),
           sum(len(v) for v in by_page.values())))


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2
    convert(sys.argv[1], sys.argv[2], sys.argv[3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
