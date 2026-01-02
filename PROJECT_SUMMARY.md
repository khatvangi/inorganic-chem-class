# Project Summary (Inorganic Chemistry Course)

This project builds a full interactive course experience for inorganic chemistry, focused on coordination chemistry. It includes multiple chapter game pages, a lecture series with animations and interactive visuals, and extracted figures from the LibreTexts PDF bundle. All pages are web-based (HTML/CSS/JS) and wired together with navigation.

## Top-Level Pages (Games)

- `index.html`
  - Chapter 1: Nomenclature Sprint (name the complexes).
  - Links to Chapters 2, 3, 4, and 12 games + Lectures index.
  - Intro rules + charts from PDF.

- `coordination.html`
  - Chapter 2: Coordination Numbers and Structures.
  - Modules: Geometry Match, Build the Sphere, Ambiguity Challenge, Rare Structures Lab.
  - Intro rules + charts from PDF.

- `isomerism.html`
  - Chapter 3: Isomerism Lab.
  - Modes: Geometric (cis/trans, fac/mer), Optical (Lambda/Delta), Structural isomer classification.
  - Uses chart images from PDF.

- `bonding.html`
  - Chapter 4: Bonding + Ligand Field Theory.
  - Modes: Orbital Builder, Spectrochemical Sprint, MO Diagram Builder, Spectra Challenge.
  - Includes charts from PDF; MO diagram builder with energy ladder.

- `reactions.html`
  - Chapter 12: Reactions and Mechanisms Lab.
  - Modes: Rate Law Detective, Pathway Predictor, Stereo Outcome.
  - Includes reaction mechanism visuals from PDF.

## Game Logic (JavaScript)

- `app.js`
  - Chapter 1 logic: naming questions, strict IUPAC checks, adaptive reinforcement, difficulty tiers (intro/core/advanced), isomer compare toggle, 3D model rendering with 3Dmol.js, label toggles, color modes, and rigor mode (auto-lock labels after mastery).

- `coordination.js`
  - Chapter 2 logic: CN/geometry questions, build and ambiguity modes, adaptive queue, and idealized 3D models with 3Dmol.js (geometry maps for CN 2-8).

- `isomerism.js`
  - Chapter 3 logic: geometric + optical + structural isomer identification.
  - Compare toggle, mirror view for optical isomers, adaptive reinforcement, label lock for rigor mode.

- `bonding.js`
  - Chapter 4 logic:
    - Orbital Builder: draggable electrons into orbital slots + CFSE and pairing count.
    - Spectrochemical Sprint: clickable ordering.
    - MO Diagram Builder: drag t2g/eg onto an energy ladder, with sigma/pi/t2g/eg labels and shaded overlap bands.
    - Spectra questions.

- `reactions.js`
  - Chapter 12 logic: mechanism classification (D/I/A), pathway prediction, stereo outcome questions.
  - Adaptive queue and basic session stats.

## Shared Styling

- `styles.css`
  - Main site styles for game pages, cards, charts, toggles, 3D panels, option grids, and new orbital/CFSE widgets.
  - Added components for:
    - Chapter intro cards
    - Chart grids
    - Orbital slots, electron bank, CFSE panel
    - MO diagram columns + shaded overlap bands

## Lecture Series (Web Pages)

Folder: `lectures/`

- `lectures/index.html`
  - Lecture hub with weekly schedule.

- `lectures/lecture-9-3-nomenclature.html`
  - 75-minute lecture page for nomenclature; includes charts and micro-demo animations.

- `lectures/lecture-9-5-coordination.html`
  - 75-minute lecture page for coordination numbers and structures; charts + toggles + micro-demos.

- `lectures/lecture-9-4-isomerism.html`
  - 75-minute lecture page for isomerism; charts + toggles + micro-demos.

- `lectures/lecture-10-bonding.html`
  - 75-minute lecture page for bonding/LFT; charts + interactive sorters + micro-demos.

- `lectures/lecture-12-reactions.html`
  - 75-minute lecture page for reactions and mechanisms; charts + toggles + micro-demos.

- `lectures/lecture.css`
  - Lecture layout, typography, cards, reveal animation, demos, sorters.

- `lectures/lecture.js`
  - Reveal-on-scroll, steppers, toggles, sortable interactions, and auto-playing micro-demos.

## Extracted Figure Assets (from PDF bundle)

All figures were extracted from the textbook ZIP using `pdfimages`.

- Nomenclature: `assets/nomenclature/`
  - `fig-079.png` (naming workflow)
  - `fig-005.png` (ligand denticity examples)

- Coordination numbers: `assets/coordination/`
  - `fig-004.png` (CN geometries)
  - `fig-006.png` (Kepert preferred geometries)
  - `fig-002.png` (metal preferences)

- Isomerism: `assets/isomerism/`
  - `fig-002.png` (Figure 9.4.1 isomerism map)
  - `fig-018.png` (Lambda/Delta examples)

- Bonding/LFT: `assets/bonding/`
  - `fig-10-3-2-018.png` (splitting / spin diagram)
  - `fig-10-3-1-016.png` (metal/ligand energy match)
  - `fig-10-4-4-008.png` (spectrochemical series)
  - `fig-10-3-4-001.png` (tetrahedral field)
  - `fig-10-3-5-001.png` (square planar field)

- Reactions: `assets/reactions/`
  - `sq-004.png` (square planar associative TS)
  - `oct-001.png` (octahedral stereochemical pathways)

## Navigation

- All game pages link to each other where relevant.
- `index.html` links to all chapters and the lecture hub.
- Lecture pages link back to lecture index and relevant game pages.

## External Libraries

- 3Dmol.js (CDN) is used for 3D models in game pages:
  - `index.html`, `coordination.html`, `isomerism.html`.

## Notable Behaviors

- Adaptive reinforcement queues similar questions after incorrect answers.
- Rigor mode locks labels after mastery thresholds in chapters 1-3.
- Bonding chapter shows CFSE + pairing energy and supports interactive MO building with overlap shading.

