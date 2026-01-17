# Project Summary (Inorganic Chemistry Course) - Modernized

This project is a full interactive course experience for inorganic chemistry, focusing on coordination chemistry and solid state. It features a suite of game-based drills and an integrated lecture series.

## Architecture & Tech Stack

- **Drawing Engine:** ChemDoodle Web Components (Replaced 3Dmol.js).
- **Frontend:** Vanilla HTML5, CSS3 (Modern Grid/Flexbox), and ES Modules.
- **State Management:** Localized state with `localStorage` persistence, shared via `js/utils.js`.
- **Data Driven:** Content is externalized into JSON files in `data/` for easy updates and scalability.
- **Accessibility:** Keyboard-navigable interactions for drag-and-drop components.

## Directory Structure

- `data/`: JSON question banks for all chapters.
- `js/`: Shared utility functions (`utils.js`).
- `libs/`: External libraries (ChemDoodleWeb.js, ChemDoodleWeb.css).
- `lectures/`: Integrated slide deck for each chapter.
- `assets/`: Figure extracts and PDFs from textbook sources.

## Core Modules (Games)

- **Nomenclature Sprint (`index.html` / `app.js`)**
  - IUPAC naming for complex cations, anions, and neutral species.
  - Supports 2D and 3D molecular views using ChemDoodle.
  
- **Structures Lab (`coordination.html` / `coordination.js`)**
  - Coordination number inference and geometry mapping.
  - Interactive 3D geometry recognition (CN 2-8).

- **Isomerism Lab (`isomerism.html` / `isomerism.js`)**
  - Geometric (cis/trans, fac/mer) and Optical (Lambda/Delta) identification.
  - Mirror-view toggle for enantiomer comparison.

- **Bonding + LFT (`bonding.html` / `bonding.js`)**
  - Orbital Builder: Interactive electron placement with CFSE calculation.
  - MO Match Lab: Build energy ladders for sigma/pi donor/acceptor sets.
  - Spectrochemical series sorting.

- **Reactions Lab (`reactions.html` / `reactions.js`)**
  - Substitution mechanism diagnosis (D/I/A).
  - Rate law and stereochemical outcome prediction.

- **Solids Lab (`solids.html` / `solids.js`)**
  - Unit cell ID, atom counting, and packing efficiency drills.

## Key Features

- **Adaptive Reinforcement:** Incorrect answers trigger similar questions from the bank.
- **Rigor Mode:** Automatically hides labels and increases difficulty once mastery thresholds are met.
- **Keyboard Access:** All drag-and-drop interactions support Tab/Enter/Space navigation.
- **Cross-Chapter Navigation:** Integrated hub and lateral links between related topics.

## Maintenance

- To update questions, edit the corresponding `.json` file in the `data/` directory.
- Shared logic (scoring, normalization, persistence) is central in `js/utils.js`.