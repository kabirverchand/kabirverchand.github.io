#!/usr/bin/env python3
from html import escape
from pathlib import Path
import re

ROOT = Path(__file__).parent
CONTENT = ROOT / "content.md"


def parse_front_matter(text):
    if not text.startswith("---\n"):
        return {}, text

    end = text.find("\n---", 4)
    if end == -1:
        return {}, text

    raw_meta = text[4:end].strip()
    body = text[end + 4 :].strip()
    meta = {}

    for line in raw_meta.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()

    return meta, body


def split_sections(markdown):
    matches = list(re.finditer(r"^##\s+(.+)$", markdown, flags=re.MULTILINE))
    sections = {}

    for index, match in enumerate(matches):
        heading = match.group(1).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        sections[heading] = markdown[start:end].strip()

    return sections


def markdown_to_html(markdown):
    html = []
    paragraph = []
    list_type = None

    def close_paragraph():
        nonlocal paragraph
        if paragraph:
            html.append(f"<p>{inline(' '.join(paragraph))}</p>")
            paragraph = []

    def close_list():
        nonlocal list_type
        if list_type:
            html.append(f"</{list_type}>")
            list_type = None

    for raw_line in markdown.splitlines():
        line = raw_line.strip()

        if not line:
            close_paragraph()
            close_list()
            continue

        heading = re.match(r"^(#{3,4})\s+(.+)$", line)
        if heading:
            close_paragraph()
            close_list()
            level = len(heading.group(1))
            html.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", line)
        if unordered:
            close_paragraph()
            if list_type != "ul":
                close_list()
                html.append("<ul>")
                list_type = "ul"
            html.append(f"<li>{inline(unordered.group(1))}</li>")
            continue

        ordered = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered:
            close_paragraph()
            if list_type != "ol":
                close_list()
                html.append("<ol>")
                list_type = "ol"
            html.append(f"<li>{inline(ordered.group(1))}</li>")
            continue

        close_list()
        paragraph.append(line)

    close_paragraph()
    close_list()
    return "\n".join(html)


def inline(text):
    text = escape(text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", text)
    return text


def link(match):
    label = match.group(1)
    href = escape(match.group(2), quote=True)
    return f'<a href="{href}">{label}</a>'


def header(meta, active):
    name = escape(meta.get("name", "Your Name"))
    pages = [
        ("index.html", "Home", "home"),
        ("research.html", "Research", "research"),
        ("teaching.html", "Teaching", "teaching"),
    ]
    nav_items = []
    for href, label, key in pages:
        class_name = ' class="active"' if key == active else ""
        nav_items.append(f'          <a href="{href}"{class_name}>{label}</a>')
    nav = "\n".join(nav_items)

    return f"""    <header class="site-header">
      <h1 class="site-title"><a href="index.html">{name}</a></h1>
      <nav class="tabs" aria-label="Primary navigation">
{nav}
      </nav>
    </header>"""


def page(meta, active, title, body):
    name = escape(meta.get("name", "Your Name"))
    page_title = f"{escape(title)} | {name}" if title else name
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{page_title}</title>
    <link rel="stylesheet" href="styles.css">
  </head>
  <body>
    <div class="site">
{header(meta, active)}
      <main>
{body}
      </main>
    </div>
  </body>
</html>
"""


def homepage(meta, sections):
    name = escape(meta.get("name", "Your Name"))
    photo = escape(meta.get("photo", "assets/profile-placeholder.svg"), quote=True)
    intro = intro_block(meta)

    body = f"""        <section class="intro">
          <figure class="intro-photo">
            <img src="{photo}" alt="Profile photo of {name}">
          </figure>
{intro}
        </section>

        <section class="content-section">
          <h3>Biosketch</h3>
{markdown_to_html(sections.get("Bio", ""))}
        </section>

        <section class="content-section publications">
          <h3>Selected Publications</h3>
{markdown_to_html(sections.get("Selected Publications", ""))}
        </section>"""
    return body


def intro_block(meta):
    title = meta.get("title", "")
    affiliation = meta.get("affiliation", "")
    location = meta.get("location", "")
    email = meta.get("email", "")
    office = meta.get("office", "")
    lines = []

    if title:
        lines.append(escape(title))
    if affiliation:
        lines.append(escape(affiliation))
    if location:
        lines.append(escape(location))

    if email:
        safe_email = escape(email)
        safe_href = escape(email, quote=True)
        lines.append(f'Email: <a href="mailto:{safe_href}">{safe_email}</a>')
    if office:
        lines.append(f"Office: {escape(office)}")

    if not lines:
        return ""

    return f"""          <div class="intro-text">
            <p>{"<br>".join(lines)}</p>
          </div>"""


def section_page(section_name, sections):
    return f"""        <h1>{escape(section_name)}</h1>
{markdown_to_html(sections.get(section_name, ""))}"""


def main():
    meta, body = parse_front_matter(CONTENT.read_text())
    sections = split_sections(body)

    (ROOT / "index.html").write_text(page(meta, "home", "", homepage(meta, sections)))
    (ROOT / "research.html").write_text(page(meta, "research", "Research", section_page("Research", sections)))
    (ROOT / "teaching.html").write_text(page(meta, "teaching", "Teaching", section_page("Teaching", sections)))


if __name__ == "__main__":
    main()
