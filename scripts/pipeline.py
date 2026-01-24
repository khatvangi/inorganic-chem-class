"""
Chapter Extraction Pipeline for CHEM 361

Extracts figures, exercises, and text from ic_tina.pdf to build lecture materials.

Usage:
    python pipeline.py extract-figures 2      # Extract figures from chapter 2
    python pipeline.py extract-figures all    # Extract figures from all chapters
    python pipeline.py extract-exercises 2    # Extract exercises from chapter 2
    python pipeline.py build-lecture 2        # Build lecture HTML for chapter 2
    python pipeline.py status                 # Show extraction status
"""

import os
import sys
import json
import re
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF

# paths
BASE_DIR = Path(__file__).parent.parent
TEXTBOOK_PATH = Path("/storage/textbooks/ic_tina.pdf")
CHAPTERS_JSON = BASE_DIR / "data" / "chapters.json"
FIGURES_DIR = BASE_DIR / "assets" / "figures"
EXERCISES_DIR = BASE_DIR / "data" / "exercises"
LECTURES_DIR = BASE_DIR / "lectures"

# figure detection settings
FIGURE_PATTERNS = [
    r"Figure\s+(\d+\.\d+)",
    r"Fig\.\s+(\d+\.\d+)",
]


def load_chapters():
    """Load chapter metadata."""
    with open(CHAPTERS_JSON) as f:
        chapters = json.load(f)
    # fix duplicate ch 25 issue
    return [ch for ch in chapters if ch["end_page"] > ch["start_page"]]


def get_chapter(num: int):
    """Get chapter by number."""
    for ch in load_chapters():
        if ch["number"] == num:
            return ch
    return None


def extract_figures_from_chapter(chapter_num: int, doc=None):
    """
    Extract figures from a chapter.

    Strategy:
    1. Find pages mentioning figure numbers
    2. Render those pages at 2x resolution
    3. Detect figure regions by analyzing whitespace/text boundaries
    4. Crop and save individual figures
    """
    ch = get_chapter(chapter_num)
    if not ch:
        print(f"Chapter {chapter_num} not found")
        return

    close_doc = doc is None
    if doc is None:
        doc = fitz.open(TEXTBOOK_PATH)

    output_dir = FIGURES_DIR / f"chapter{chapter_num}"
    output_dir.mkdir(parents=True, exist_ok=True)

    # find which figures are in this chapter
    figure_pages = {}  # fig_num -> [pages]

    start_page = ch["start_page"] - 1  # 0-indexed
    end_page = ch["end_page"]

    for page_idx in range(start_page, end_page):
        page = doc[page_idx]
        text = page.get_text()

        for pattern in FIGURE_PATTERNS:
            matches = re.findall(pattern, text)
            for fig_num in matches:
                if fig_num.startswith(f"{chapter_num}."):
                    if fig_num not in figure_pages:
                        figure_pages[fig_num] = []
                    rel_page = page_idx - start_page + 1
                    if rel_page not in figure_pages[fig_num]:
                        figure_pages[fig_num].append(rel_page)

    print(f"\nChapter {chapter_num}: {ch['title']}")
    print(f"Pages {ch['start_page']}-{ch['end_page']} ({end_page - start_page} pages)")
    print(f"Found {len(figure_pages)} figures referenced")

    # render pages with figures
    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)

    pages_with_figures = set()
    for fig, pages in figure_pages.items():
        for p in pages:
            pages_with_figures.add(p)

    # save full page renders for manual cropping reference
    pages_dir = output_dir / "pages"
    pages_dir.mkdir(exist_ok=True)

    for rel_page in sorted(pages_with_figures):
        abs_page = start_page + rel_page - 1
        page = doc[abs_page]
        pix = page.get_pixmap(matrix=mat)

        page_path = pages_dir / f"page_{rel_page}.png"
        pix.save(str(page_path))

    # create figure mapping file
    mapping = {
        "chapter": chapter_num,
        "title": ch["title"],
        "figures": {}
    }

    for fig_num in sorted(figure_pages.keys(), key=lambda x: float(x.split('.')[1])):
        mapping["figures"][fig_num] = {
            "pages": figure_pages[fig_num],
            "extracted": False,
            "file": None
        }

    mapping_path = output_dir / "mapping.json"
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=2)

    print(f"Saved {len(pages_with_figures)} page renders to {pages_dir}")
    print(f"Figure mapping saved to {mapping_path}")
    print(f"\nTo extract individual figures, run:")
    print(f"  python pipeline.py crop-figures {chapter_num}")

    if close_doc:
        doc.close()

    return mapping


def crop_figures_auto(chapter_num: int):
    """
    Attempt automatic figure cropping using simple heuristics.

    For more complex layouts, manual cropping may be needed.
    """
    output_dir = FIGURES_DIR / f"chapter{chapter_num}"
    mapping_path = output_dir / "mapping.json"

    if not mapping_path.exists():
        print(f"Run 'extract-figures {chapter_num}' first")
        return

    with open(mapping_path) as f:
        mapping = json.load(f)

    pages_dir = output_dir / "pages"

    # group figures by page
    page_figures = {}
    for fig_num, info in mapping["figures"].items():
        # use first page where figure appears
        if info["pages"]:
            page = info["pages"][0]
            if page not in page_figures:
                page_figures[page] = []
            page_figures[page].append(fig_num)

    # process each page
    for page_num, figs in page_figures.items():
        page_path = pages_dir / f"page_{page_num}.png"
        if not page_path.exists():
            continue

        img = Image.open(page_path)
        w, h = img.size

        # simple heuristic: divide page into regions based on figure count
        n_figs = len(figs)

        if n_figs == 1:
            # single figure - take middle portion
            fig_img = img.crop((0, int(h*0.1), w, int(h*0.7)))
            fig_path = output_dir / f"fig_{figs[0].replace('.', '_')}.png"
            fig_img.save(fig_path)
            mapping["figures"][figs[0]]["extracted"] = True
            mapping["figures"][figs[0]]["file"] = fig_path.name
            print(f"  Extracted {figs[0]} -> {fig_path.name}")

        elif n_figs == 2:
            # two figures - likely left/right or top/bottom
            # try left/right first
            fig1 = img.crop((0, int(h*0.05), int(w*0.5), int(h*0.55)))
            fig2 = img.crop((int(w*0.45), int(h*0.05), w, int(h*0.55)))

            for i, (fig_img, fig_num) in enumerate([(fig1, figs[0]), (fig2, figs[1])]):
                fig_path = output_dir / f"fig_{fig_num.replace('.', '_')}.png"
                fig_img.save(fig_path)
                mapping["figures"][fig_num]["extracted"] = True
                mapping["figures"][fig_num]["file"] = fig_path.name
                print(f"  Extracted {fig_num} -> {fig_path.name}")

        elif n_figs >= 3:
            # multiple figures - extract as regions
            # this is a rough approximation
            fig_height = int(h * 0.6 / ((n_figs + 1) // 2))

            for i, fig_num in enumerate(figs):
                row = i // 2
                col = i % 2

                x1 = int(w * 0.5 * col)
                x2 = int(w * 0.5 * (col + 1)) if col == 0 else w
                y1 = int(h * 0.05) + row * fig_height
                y2 = y1 + fig_height

                fig_img = img.crop((x1, y1, x2, y2))
                fig_path = output_dir / f"fig_{fig_num.replace('.', '_')}.png"
                fig_img.save(fig_path)
                mapping["figures"][fig_num]["extracted"] = True
                mapping["figures"][fig_num]["file"] = fig_path.name
                print(f"  Extracted {fig_num} -> {fig_path.name}")

    # save updated mapping
    with open(mapping_path, "w") as f:
        json.dump(mapping, f, indent=2)

    extracted = sum(1 for f in mapping["figures"].values() if f["extracted"])
    print(f"\nExtracted {extracted}/{len(mapping['figures'])} figures")


def extract_exercises_from_chapter(chapter_num: int, doc=None):
    """
    Extract exercises from chapter end.

    Exercises appear near the end in sections:
    - "Exercises" (shorter questions)
    - "Tutorial problems" (longer, essay-style)

    Format: "2.4 What shapes would you expect for..."
    """
    ch = get_chapter(chapter_num)
    if not ch:
        print(f"Chapter {chapter_num} not found")
        return

    close_doc = doc is None
    if doc is None:
        doc = fitz.open(TEXTBOOK_PATH)

    output_dir = EXERCISES_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    start_page = ch["start_page"] - 1
    end_page = ch["end_page"]

    exercises = []
    tutorial_problems = []
    in_exercises = False
    in_tutorials = False
    current_item = None
    current_list = exercises

    # start from near the end of the chapter (exercises are usually last 5-10 pages)
    search_start = max(start_page, end_page - 10)

    for page_idx in range(search_start, end_page):
        page = doc[page_idx]
        text = page.get_text()

        # detect sections
        if "Exercises" in text and not in_exercises:
            in_exercises = True
            current_list = exercises

        if "TUTORIAL PROBLEMS" in text or "Tutorial problems" in text:
            in_tutorials = True
            current_list = tutorial_problems

        if in_exercises or in_tutorials:
            lines = text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # skip section headers
                if line in ["Exercises", "EXERCISES", "TUTORIAL PROBLEMS", "Tutorial problems"]:
                    continue

                # match exercise numbers: "2.4 What shapes..." or "2.14 Rationalize..."
                # exercises have format: chapter.number followed by question text
                match = re.match(rf"^{chapter_num}\.(\d+)\s+(.+)", line)
                if match:
                    # save previous item
                    if current_item and len(current_item["text"]) > 10:
                        current_list.append(current_item)

                    ex_num = f"{chapter_num}.{match.group(1)}"
                    current_item = {
                        "number": ex_num,
                        "text": match.group(2),
                        "type": "tutorial" if in_tutorials else "exercise",
                        "page": page_idx - start_page + 1
                    }
                elif current_item and line:
                    # continuation - but skip if it's a new chapter header
                    if not re.match(r"^\d+\s+[A-Z]", line) and not line.startswith("Further reading"):
                        current_item["text"] += " " + line

    # save last item
    if current_item and len(current_item["text"]) > 10:
        current_list.append(current_item)

    # combine and save
    all_items = exercises + tutorial_problems

    output_path = output_dir / f"chapter{chapter_num}.json"
    with open(output_path, "w") as f:
        json.dump({
            "chapter": chapter_num,
            "title": ch["title"],
            "exercises": [e for e in all_items if e["type"] == "exercise"],
            "tutorial_problems": [e for e in all_items if e["type"] == "tutorial"]
        }, f, indent=2)

    n_ex = len([e for e in all_items if e["type"] == "exercise"])
    n_tut = len([e for e in all_items if e["type"] == "tutorial"])
    print(f"Chapter {chapter_num}: {n_ex} exercises, {n_tut} tutorial problems")
    print(f"Saved to {output_path}")

    if close_doc:
        doc.close()

    return all_items


def extract_chapter_text(chapter_num: int, doc=None):
    """
    Extract structured text from a chapter.
    Returns sections with headers and paragraphs.
    """
    ch = get_chapter(chapter_num)
    if not ch:
        return None

    close_doc = doc is None
    if doc is None:
        doc = fitz.open(TEXTBOOK_PATH)

    start_page = ch["start_page"] - 1
    end_page = ch["end_page"] - 5  # skip exercises at end

    sections = []
    current_section = None

    for page_idx in range(start_page, end_page):
        page = doc[page_idx]
        blocks = page.get_text("dict")["blocks"]

        for block in blocks:
            if "lines" not in block:
                continue

            for line in block["lines"]:
                text = "".join([span["text"] for span in line["spans"]]).strip()
                if not text:
                    continue

                # detect section headers (larger font, specific patterns)
                font_size = line["spans"][0]["size"] if line["spans"] else 10

                # section header patterns
                is_header = False
                if font_size > 11 and re.match(r"^\d+\.\d+\s+[A-Z]", text):
                    is_header = True
                elif font_size > 12 and re.match(r"^[A-Z][a-z]+\s+[a-z]", text):
                    is_header = True
                elif text.startswith("KEY POINT"):
                    is_header = True

                if is_header:
                    if current_section:
                        sections.append(current_section)
                    current_section = {
                        "header": text,
                        "paragraphs": [],
                        "figures": []
                    }
                elif current_section:
                    # check for figure references
                    fig_matches = re.findall(r"Fig(?:ure)?\.?\s*(\d+\.\d+)", text)
                    for fig_num in fig_matches:
                        if fig_num not in current_section["figures"]:
                            current_section["figures"].append(fig_num)

                    current_section["paragraphs"].append(text)

    if current_section:
        sections.append(current_section)

    if close_doc:
        doc.close()

    return sections


def build_lecture(chapter_num: int):
    """
    Build an HTML lecture from extracted content.
    """
    ch = get_chapter(chapter_num)
    if not ch:
        print(f"Chapter {chapter_num} not found")
        return

    print(f"Building lecture for Chapter {chapter_num}: {ch['title']}")

    # load figure mapping
    fig_dir = FIGURES_DIR / f"chapter{chapter_num}"
    mapping_path = fig_dir / "mapping.json"

    figures = {}
    if mapping_path.exists():
        with open(mapping_path) as f:
            mapping = json.load(f)
        figures = mapping.get("figures", {})

    # load exercises
    ex_path = EXERCISES_DIR / f"chapter{chapter_num}.json"
    exercises = []
    tutorials = []
    if ex_path.exists():
        with open(ex_path) as f:
            data = json.load(f)
        exercises = data.get("exercises", [])
        tutorials = data.get("tutorial_problems", [])

    # extract text sections
    doc = fitz.open(TEXTBOOK_PATH)
    sections = extract_chapter_text(chapter_num, doc)
    doc.close()

    if not sections:
        print(f"  No sections extracted")
        return

    print(f"  {len(sections)} sections, {len(figures)} figures, {len(exercises)} exercises")

    # generate HTML
    html = generate_lecture_html(chapter_num, ch["title"], sections, figures, exercises, tutorials)

    # save
    LECTURES_DIR.mkdir(exist_ok=True)
    output_path = LECTURES_DIR / f"lecture{chapter_num}.html"
    with open(output_path, "w") as f:
        f.write(html)

    print(f"  Saved to {output_path}")
    return output_path


def generate_lecture_html(chapter_num, title, sections, figures, exercises, tutorials):
    """Generate the HTML for a lecture."""

    # build figure HTML snippets
    def figure_html(fig_num):
        fig_key = fig_num
        if fig_key in figures and figures[fig_key].get("extracted"):
            fig_file = figures[fig_key]["file"]
            return f'''
            <div class="figure">
                <img src="../assets/figures/chapter{chapter_num}/{fig_file}" alt="Figure {fig_num}">
                <div class="figure-caption"><strong>Figure {fig_num}</strong></div>
            </div>'''
        return ""

    # build sections HTML
    sections_html = ""
    for i, section in enumerate(sections[:20], 1):  # limit sections for readability
        header = section["header"]
        paragraphs = section["paragraphs"]

        # clean header
        header_clean = re.sub(r"^\d+\.\d+\s*", "", header)

        sections_html += f'''
        <section class="section" id="section-{i}">
            <h2>{header_clean}</h2>
'''
        # add paragraphs, inserting figures where referenced
        shown_figures = set()
        for para in paragraphs[:10]:  # limit paragraphs
            if len(para) > 50:  # skip short fragments
                sections_html += f"            <p>{para}</p>\n"

            # insert figures referenced in this paragraph
            for fig_num in section["figures"]:
                if fig_num not in shown_figures:
                    fig_html_str = figure_html(fig_num)
                    if fig_html_str:
                        sections_html += fig_html_str
                        shown_figures.add(fig_num)

        sections_html += "        </section>\n"

    # build exercises HTML
    exercises_html = ""
    if exercises or tutorials:
        exercises_html = '''
        <section class="section" id="exercises">
            <h2>Exercises</h2>
            <div class="exercise-list">
'''
        for ex in exercises[:15]:
            exercises_html += f'''
                <div class="exercise">
                    <strong>{ex["number"]}</strong> {ex["text"][:300]}{"..." if len(ex["text"]) > 300 else ""}
                </div>
'''
        exercises_html += "            </div>\n        </section>\n"

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lecture {chapter_num}: {title} | CHEM 361</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
    <style>
        :root {{
            --bg: #0a0f1a;
            --bg-card: #131b2e;
            --bg-elevated: #1a2540;
            --text: #e8eaed;
            --text-dim: #9aa0a6;
            --accent: #8ab4f8;
            --accent-green: #81c995;
            --accent-yellow: #fdd663;
            --accent-purple: #c58af9;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; }}

        body {{
            font-family: 'Crimson Pro', Georgia, serif;
            background: var(--bg);
            color: var(--text);
            font-size: 1.15rem;
            line-height: 1.95;
        }}

        .lecture {{
            max-width: 900px;
            margin: 0 auto;
            padding: 3rem 2rem 6rem;
        }}

        .nav {{
            display: flex;
            justify-content: space-between;
            padding: 1rem 2rem;
            background: var(--bg-card);
            border-bottom: 1px solid var(--bg-elevated);
        }}

        .nav a {{
            color: var(--text-dim);
            text-decoration: none;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
        }}

        .nav a:hover {{ color: var(--accent); }}

        .lecture-header {{
            text-align: center;
            margin-bottom: 3rem;
            padding-bottom: 2rem;
            border-bottom: 1px solid #2a3a5a;
        }}

        .lecture-header h1 {{
            font-size: 2.4rem;
            font-weight: 500;
            color: var(--accent);
        }}

        .section {{ margin-bottom: 3rem; }}

        h2 {{
            font-size: 1.5rem;
            color: var(--accent-purple);
            margin-bottom: 1.2rem;
            font-weight: 500;
        }}

        p {{ margin-bottom: 1.2rem; text-align: justify; }}

        .figure {{
            margin: 2rem 0;
            background: var(--bg-card);
            border-radius: 12px;
            overflow: hidden;
            text-align: center;
        }}

        .figure img {{
            max-width: 100%;
            max-height: 500px;
            object-fit: contain;
            background: #f8f8f8;
            padding: 1rem;
        }}

        .figure-caption {{
            padding: 1rem;
            background: var(--bg-elevated);
            font-size: 0.95rem;
            color: var(--text-dim);
        }}

        .exercise-list {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .exercise {{
            background: var(--bg-card);
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border-left: 3px solid var(--accent-green);
        }}

        .exercise strong {{
            color: var(--accent-green);
            font-family: 'JetBrains Mono', monospace;
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <a href="../index.html">← CHEM 361</a>
        <a href="index.html">All Lectures</a>
    </nav>

    <main class="lecture">
        <header class="lecture-header">
            <h1>Lecture {chapter_num}: {title}</h1>
        </header>

{sections_html}
{exercises_html}
    </main>

    <script>
        document.addEventListener("DOMContentLoaded", function() {{
            renderMathInElement(document.body, {{
                delimiters: [
                    {{left: '$$', right: '$$', display: true}},
                    {{left: '$', right: '$', display: false}},
                    {{left: '\\\\(', right: '\\\\)', display: false}},
                    {{left: '\\\\[', right: '\\\\]', display: true}}
                ]
            }});
        }});
    </script>
</body>
</html>'''

    return html


def show_status():
    """Show extraction status for all chapters."""
    chapters = load_chapters()

    print(f"{'Ch':<4} {'Title':<45} {'Figures':<12} {'Exercises':<12}")
    print("-" * 75)

    for ch in chapters:
        num = ch["number"]
        title = ch["title"][:42]

        # check figures
        fig_dir = FIGURES_DIR / f"chapter{num}"
        mapping_path = fig_dir / "mapping.json"
        if mapping_path.exists():
            with open(mapping_path) as f:
                mapping = json.load(f)
            total = len(mapping["figures"])
            extracted = sum(1 for f in mapping["figures"].values() if f.get("extracted"))
            fig_status = f"{extracted}/{total}"
        else:
            fig_status = "-"

        # check exercises
        ex_path = EXERCISES_DIR / f"chapter{num}.json"
        if ex_path.exists():
            with open(ex_path) as f:
                data = json.load(f)
            ex_status = str(len(data.get("exercises", [])))
        else:
            ex_status = "-"

        print(f"{num:<4} {title:<45} {fig_status:<12} {ex_status:<12}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return

    cmd = sys.argv[1]

    if cmd == "extract-figures":
        if len(sys.argv) < 3:
            print("Usage: pipeline.py extract-figures <chapter_num|all>")
            return

        target = sys.argv[2]
        doc = fitz.open(TEXTBOOK_PATH)

        if target == "all":
            for ch in load_chapters():
                extract_figures_from_chapter(ch["number"], doc)
                print()
        else:
            extract_figures_from_chapter(int(target), doc)

        doc.close()

    elif cmd == "crop-figures":
        if len(sys.argv) < 3:
            print("Usage: pipeline.py crop-figures <chapter_num>")
            return
        crop_figures_auto(int(sys.argv[2]))

    elif cmd == "extract-exercises":
        if len(sys.argv) < 3:
            print("Usage: pipeline.py extract-exercises <chapter_num|all>")
            return

        target = sys.argv[2]
        doc = fitz.open(TEXTBOOK_PATH)

        if target == "all":
            for ch in load_chapters():
                extract_exercises_from_chapter(ch["number"], doc)
        else:
            extract_exercises_from_chapter(int(target), doc)

        doc.close()

    elif cmd == "build-lecture":
        if len(sys.argv) < 3:
            print("Usage: pipeline.py build-lecture <chapter_num|all>")
            return

        target = sys.argv[2]
        if target == "all":
            for ch in load_chapters():
                build_lecture(ch["number"])
        else:
            build_lecture(int(target))

    elif cmd == "status":
        show_status()

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
