#!/usr/bin/env python3
"""
md_to_html_template.py

Convert a very small subset of Markdown (section headers + strophes) into
the HTML layout you asked for, wrapped inside the exact template you gave.
"""

import sys
from pathlib import Path


def split_strophes(lines):
    """Turn raw lines of a section into strophe blocks (<div class="strophe">)."""
    strophes = []
    cur = []

    for raw in lines:
        line = raw.rstrip("\n")
        if line.strip() == "":
            if cur:                       # end of a stanza
                strophes.append("<br>".join(cur))
                cur = []
        else:
            cur.append(line)

    if cur:                               # last stanza (if file didn't end with an empty line)
        strophes.append("<br>".join(cur))

    return strophes


def parse_markdown(lines):
    """
    Return a list of pairs.
    Each pair contains an original section and its translation.
    Titles are stored **without** leading # or ##.
    """
    pairs = []
    current_pair = None
    section_key = None   # "original" or "translation"

    for raw in lines:
        line = raw.rstrip("\n")

        if line.startswith("#"):
            level = len(line) - len(line.lstrip('#'))
            title = line.lstrip('#').strip()          # <-- strip the hash characters

            if level == 1:                            # original section
                current_pair = {
                    "original": {"title": title, "raw_lines": []},
                    "translation": None,
                }
                pairs.append(current_pair)
                section_key = "original"

            elif level == 2:                          # translation section
                if current_pair is None:
                    raise ValueError("Translation header without preceding original.")
                current_pair["translation"] = {"title": title, "raw_lines": []}
                section_key = "translation"
            else:
                continue

        else:
            if section_key and current_pair:
                current_pair[section_key]["raw_lines"].append(line)

    return pairs


def pair_to_html(pair):
    """Turn a single pair dict into its HTML representation."""
    html = ['<div class="pair">']

    # Original (h1)
    orig = pair["original"]
    strophes = split_strophes(orig["raw_lines"])
    html.append('  <section>')
    html.append(f'    <h2>{orig["title"]}</h2>')
    for s in strophes:
        html.append(f'    <div class="strophe">{s}</div>')
    html.append('  </section>')

    # Translation (h2) – may be None
    tr = pair.get("translation")
    if tr:
        strophes = split_strophes(tr["raw_lines"])
        html.append('  <section>')
        html.append(f'    <h2>{tr["title"]}</h2>')
        for s in strophes:
            html.append(f'    <div class="strophe">{s}</div>')
        html.append('  </section>')

    html.append('</div>')
    return "\n".join(html)


def main(argv):
    if len(argv) < 2:
        print("Usage: python md_to_html_template.py input.md > output.html", file=sys.stderr)
        sys.exit(1)

    infile = Path(argv[1])
    raw_text = infile.read_text(encoding="utf-8").splitlines(True)

    pairs = parse_markdown(raw_text)
    parts_html = [pair_to_html(p) for p in pairs]

    print("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Letras - Lyrics</title>
  <link rel="stylesheet" href="style.css">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
</head>
<body>
  <div class="container">
    <div class="content">

      <img src="grupo.png" width="200px" alt="Angoleiros do Mar Logo">

      <!-- PARTS -->""")

    for part in parts_html:
        print(part)

    # close the remaining tags
    print("""    </div>
  </div>
</body>
</html>""")


if __name__ == "__main__":
    main(sys.argv)
