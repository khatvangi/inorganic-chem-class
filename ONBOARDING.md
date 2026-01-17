# Onboarding & Technical Manual

**Target Audience:** LLM Agents, Developers, and Automated Tools.
**Last Updated:** January 17, 2026
**Status:** Modernized, Data-Driven, ES Modules.

## 1. Project Overview
This repository contains a lightweight, interactive web application for **CHEM 361: Inorganic Chemistry**. It includes game-based learning modules (drills) and lecture slides. The application runs entirely in the browser using vanilla HTML, CSS, and JavaScript, with **no build step** required.

**Live Site:** https://chem361.thebeakers.com
**Sister Course:** https://chem291.thebeakers.com (Math for Chemistry)
**Deployment:** Cloudflare Pages (auto-deploy from GitHub)

## 2. Technical Stack
-   **Core:** HTML5, CSS3, JavaScript (ES6+ Modules).
-   **Rendering Engine:** [ChemDoodle Web Components](https://web.chemdoodle.com/) (v11.0.0) for 2D and 3D molecular visualization.
    -   *Note:* Replaced the legacy `3Dmol.js` engine.
-   **Data Storage:** Static JSON files (fetched at runtime).
-   **Persistence:** `localStorage` for saving user progress and settings.
-   **Styling:** CSS Variables, Flexbox/Grid (in `styles.css`).

## 3. Directory Structure & Key Artifacts

```text
/
├── index.html              # Landing page (single-card, purple theme)
├── sprint.html             # Chapter 1: Nomenclature Sprint
├── coordination.html       # Chapter 2: Structures & Geometry
├── isomerism.html          # Chapter 3: Isomerism (Geometric/Optical)
├── bonding.html            # Chapter 4: Bonding, LFT, MO Theory
├── symmetry.html           # Chapter 5: Symmetry Gallery
├── solids.html             # Chapter 7: Solid State
├── reactions.html          # Chapter 12: Mechanisms & Kinetics
├── quiz.html               # Quiz mode
├── styles.css              # Global styles (UI, layout, breadcrumb nav)
├── app.js                  # Logic for Nomenclature Sprint
├── bonding.js              # Logic for Orbital Builder/MO Match
├── coordination.js         # Logic for Geometry Match/3D Viewer
├── isomerism.js            # Logic for Isomer identification
├── reactions.js            # Logic for Kinetics/Mechanisms
├── solids.js               # Logic for Unit Cell drills
│
├── data/                   # [CRITICAL] Question banks (JSON)
│   ├── nomenclature.json
│   ├── coordination.json
│   ├── isomerism.json
│   ├── bonding.json
│   ├── reactions.json
│   └── solids.json
│
├── js/                     # Shared Logic
│   └── utils.js            # State management, UI helpers, Normalization
│
├── libs/                   # 3rd Party Libraries (Self-hosted)
│   ├── ChemDoodleWeb.js    # Core Engine
│   └── ChemDoodleWeb.css   # Engine Styles
│
├── assets/                 # Static Images & PDFs (Textbook figures)
└── lectures/               # Standalone Lecture Slides (HTML)
```

## 3.1 Navigation Pattern

All chapter pages follow a consistent navigation structure:

```
┌─────────────────────────────────────┐
│ CHEM 361 / Ch 4                     │  ← breadcrumb (course-nav)
├─────────────────────────────────────┤
│  Chapter 4                          │
│  Bonding and Ligand Field Theory    │  ← hero content
│  [Ch 1: Nomenclature] [Ch 3: ...]   │  ← related chapter links
└─────────────────────────────────────┘
```

- **Breadcrumb nav**: `styles.css` defines `.course-nav` with `.nav-breadcrumb`
- **Landing page**: Single-card design with chapter grid navigation
- **Chapter links**: Hero actions provide quick jumps to related chapters

## 4. Architectural Patterns

### A. Data-Driven Logic
Logic is strictly separated from content.
-   **Pattern:** `fetch('./data/chapter.json')` -> `state.questions` -> `render()`.
-   **Action:** To add/edit questions, **do not** touch the JavaScript files. Edit the corresponding JSON file in `data/`.

### B. Shared State Management
All modules import from `js/utils.js`.
-   **`loadSettings(key, default)`**: Hydrates state from `localStorage`.
-   **`saveSettings(key, state)`**: Persists preferences (Rigor Mode, Dark Mode, etc.).
-   **`normalizeAnswer(str)`**: Standardizes input for fuzzy matching.

### C. Molecular Rendering (ChemDoodle)
We use `ChemDoodle.ViewerCanvas` (2D) and `ChemDoodle.ViewerCanvas3D` (3D).
-   **Dynamic Generation:** Instead of loading `.mol` files, we often generate structures programmatically using `buildMolecule()` functions within the game scripts based on JSON parameters (e.g., geometry type, ligand list).
-   **Initialization:** The library must be loaded via `<script>` in the HTML head before the module script runs.

## 5. Game Modules Logic

| Module | Key Logic File | Features |
| :--- | :--- | :--- |
| **Nomenclature** | `app.js` | Text input validation, 2D/3D toggle, adaptive queue. |
| **Structures** | `coordination.js` | 3D geometry generation based on CN, ambiguity resolution. |
| **Isomerism** | `isomerism.js` | Cis/Trans & Fac/Mer generation, Mirror mode toggle. |
| **Bonding** | `bonding.js` | **Drag-and-Drop** (Orbital filling, MO diagrams), CFSE calc. |
| **Reactions** | `reactions.js` | Multiple choice logic for Rate Laws and Stereochemistry. |
| **Solids** | `solids.js` | Static image identification, numerical inputs. |

## 6. Development Guidelines

1.  **Running Locally:**
    Because the app uses ES Modules and `fetch` requests for JSON, you **cannot** open `index.html` directly via the file protocol (`file://`).
    *   **Requirement:** Use a local web server (e.g., `python3 -m http.server`, `npx http-server`, or VS Code Live Server).

2.  **Modifying Content:**
    *   Open `data/<chapter>.json`.
    *   Add a new object following the existing schema.
    *   **Tags:** Ensure `tags` are correct if you want the Adaptive Learning system to pick up the new question when a user fails a similar one.

3.  **Adding Features:**
    *   Check `js/utils.js` first to see if a helper already exists.
    *   Import utilities: `import { ... } from "./js/utils.js";`.
    *   Keep logic modular.

## 7. Known Constraints
-   **ChemDoodle License:** The library in `libs/` is the GPL version (or trial). Ensure compliance if deploying publicly.
-   **Browser Support:** Requires a modern browser supporting ES6 Modules and WebGL (for 3D).

## 8. Automated Quiz Generation
The project includes a pipeline for generating high-quality quizzes from the textbook knowledge base.

*   **Config:** `data/quiz_config.json` defines modules and topics.
*   **Script:** `generate_quizzes.py` performs RAG (Retrieval Augmented Generation):
    1.  Embeds the topic string.
    2.  Queries the `textbooks_chunks` Qdrant collection for relevant context.
        3. Prompts the LLM (Qwen3 or Gemma2) to generate a JSON-formatted question based *only* on that context.
*   **Output:** Generated quizzes are saved to `data/quizzes/*.json`.

## 9. Quick Start for Agents
If asked to "fix a bug in scoring":
1.  Read `js/utils.js` (shared scoring logic often lives here or is called from here).
2.  Read the specific game script (e.g., `app.js`).

If asked to "add a new question":
1.  Read the relevant schema in `data/`.
2.  Generate JSON entry.
3.  Write to file. No JS changes needed.
