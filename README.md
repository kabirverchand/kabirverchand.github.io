# Simple Markdown Academic Website

This is a barebones academic website generated from `content.md`.

The public pages are plain HTML and CSS. They do not load JavaScript in the browser.

## Edit Content

Update the front matter at the top of `content.md` for name, title, affiliation, email, office, and photo.

The visible page sections come from these markdown headings:

- `## Bio`
- `## Selected Publications`
- `## Research`
- `## Teaching`

To use a real profile image, place it in the `assets/` folder and update the `photo:` value in `content.md`.

## Rebuild Pages

After editing `content.md`, run:

```sh
python3 build.py
```

This regenerates:

- `index.html`
- `research.html`
- `teaching.html`

## Preview Locally

Run a local server from this folder:

```sh
python3 -m http.server 4173
```

Then open:

```text
http://localhost:4173
```

## Host On GitHub Pages

This site can be served directly by GitHub Pages from the repository root. Before pushing changes, rebuild the generated pages:

```sh
python3 build.py
```

Commit and push these files:

- `index.html`
- `research.html`
- `teaching.html`
- `styles.css`
- `content.md`
- `build.py`
- `assets/`
- `.nojekyll`

In GitHub, go to `Settings` -> `Pages`, then set:

- Source: `Deploy from a branch`
- Branch: `main`
- Folder: `/ (root)`

The site uses relative links, so it works both for a user site such as `username.github.io` and for a project site such as `username.github.io/repository-name`.
