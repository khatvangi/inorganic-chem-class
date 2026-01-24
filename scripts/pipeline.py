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

    elif cmd == "status":
        show_status()

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)


if __name__ == "__main__":
    main()
