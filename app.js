import {
  normalizeAnswer,
  loadSettings,
  saveSettings,
  updateUI,
} from "./js/utils.js";

// Global state
let questions = [];
const state = {
  currentIndex: 0,
  streak: 0,
  correct: 0,
  total: 0,
  used: new Set(),
  adaptiveQueue: [],
  adaptive: true,
  difficulty: "all",
  showLabels: true,
  colorMode: "donor",
  rigorMode: false,
  labelsLocked: false,
};

const compareState = { active: false };
const settingsKey = "coordination-naming-settings";

// UI Elements
const ui = {
  questionType: document.getElementById("questionType"),
  difficultyBadge: document.getElementById("difficultyBadge"),
  questionPrompt: document.getElementById("questionPrompt"),
  questionNote: document.getElementById("questionNote"),
  geometryHint: document.getElementById("geometryHint"),
  answerInput: document.getElementById("answerInput"),
  feedback: document.getElementById("feedback"),
  streak: document.getElementById("streak"),
  accuracy: document.getElementById("accuracy"),
  questionCount: document.getElementById("questionCount"),
  startBtn: document.getElementById("startBtn"),
  submitBtn: document.getElementById("submitBtn"),
  skipBtn: document.getElementById("skipBtn"),
  howBtn: document.getElementById("howBtn"),
  howItWorks: document.getElementById("howItWorks"),
  adaptiveToggle: document.getElementById("adaptiveToggle"),
  difficultyChips: Array.from(document.querySelectorAll(".chip[data-difficulty]")),
  compareBtn: document.getElementById("compareBtn"),
  compareLabel: document.getElementById("compareLabel"),
  viewerNote: document.getElementById("viewerNote"),
  labelToggle: document.getElementById("labelToggle"),
  colorToggle: document.getElementById("colorToggle"),
  rigorToggle: document.getElementById("rigorToggle"),
};

// ChemDoodle Viewers
let viewer2D = null;
let viewer3D = null;

// Initialization
const init = async () => {
  try {
    const response = await fetch("./data/nomenclature.json");
    questions = await response.json();
    processTags();
    
    // Load settings
    const saved = loadSettings(settingsKey, state);
    Object.assign(state, saved);
    
    // Initialize ChemDoodle
    initChemDoodle();
    
    // Setup Listeners
    setupListeners();
    
    // Initial Render
    updateUI(ui, state);
    loadQuestion();
    
  } catch (error) {
    console.error("Failed to init app:", error);
    ui.questionPrompt.textContent = "Error loading content.";
  }
};

const processTags = () => {
  const ligandTagMap = [
    { token: "NH3", tag: "ammine" },
    { token: "H2O", tag: "aqua" },
    { token: "Cl", tag: "chloro" },
    { token: "CN", tag: "cyano" },
    { token: "CO", tag: "carbonyl" },
    { token: "en", tag: "ethylenediamine" },
    { token: "NO2", tag: "nitro" },
    { token: "ONO", tag: "nitrito" },
    { token: "NCS", tag: "thiocyanato" },
    { token: "SCN", tag: "thiocyanato" },
    { token: "OH", tag: "hydroxo" },
    { token: "C2O4", tag: "oxalato" },
    { token: "acac", tag: "acac" },
    { token: "gly", tag: "glycinato" },
    { token: "mu-", tag: "bridging" },
  ];

  questions.forEach((q) => {
    if (!q.difficulty) q.difficulty = "core";
    if (!q.tags) {
      const tags = new Set();
      const formula = q.formula || "";
      tags.add(q.type.toLowerCase());
      tags.add(q.geometry.toLowerCase());
      ligandTagMap.forEach(({ token, tag }) => {
        if (formula.includes(token)) tags.add(tag);
      });
      if (formula.includes("cis-") || formula.includes("trans-")) tags.add("isomer");
      q.tags = Array.from(tags);
    }
  });
};

const initChemDoodle = () => {
  if (typeof ChemDoodle === "undefined") {
    ui.viewerNote.textContent = "ChemDoodle library not loaded.";
    return;
  }
  
  // 2D Viewer
  viewer2D = new ChemDoodle.ViewerCanvas("chemDoodle2D", 300, 300);
  viewer2D.styles.backgroundColor = "transparent";
  viewer2D.styles.atoms_font_size_2D = 14;
  viewer2D.styles.bonds_width_2D = 1.2;
  
  // 3D Viewer (replacing the old 3Dmol div)
  // We need to create a canvas for 3D if it doesn't exist, replacing #viewer3d content
  const container = document.getElementById("viewer3d");
  container.innerHTML = ""; // Clear old 3Dmol content
  const canvas3D = document.createElement("canvas");
  canvas3D.id = "chemDoodle3D";
  canvas3D.width = 300;
  canvas3D.height = 300;
  container.appendChild(canvas3D);
  
  viewer3D = new ChemDoodle.ViewerCanvas3D("chemDoodle3D", 300, 300);
  viewer3D.styles.backgroundColor = "white";
  viewer3D.styles.atoms_useJMOLColors = true;
  viewer3D.styles.bonds_color = "black";
  viewer3D.styles.bonds_cylinderDiameter_3D = 0.2;
  viewer3D.styles.atoms_sphereDiameter_3D = 0.6;
};

// Molecule Builder (Diagram -> ChemDoodle Molecule)
const buildMolecule = (diagramData, geometry) => {
  const mol = new ChemDoodle.structures.Molecule();
  
  // Center
  const centerAtom = new ChemDoodle.structures.Atom(diagramData.central || "M");
  centerAtom.x = 0; centerAtom.y = 0; centerAtom.z = 0;
  mol.atoms.push(centerAtom);
  
  const bondLength = 1.5;
  const coords = {
    // 3D Coordinates (Approximate for visual)
    top: { x: 0, y: bondLength, z: 0 },
    bottom: { x: 0, y: -bondLength, z: 0 },
    left: { x: -bondLength, y: 0, z: 0 },
    right: { x: bondLength, y: 0, z: 0 },
    front: { x: 0, y: 0, z: bondLength },
    back: { x: 0, y: 0, z: -bondLength },
    // Adjust for square planar, tetrahedral etc if needed
  };

  // Adjust coordinates based on geometry if needed
  if (geometry.toLowerCase() === "tetrahedral") {
      // Simple projection for 2D/3D
      const d = bondLength;
      coords.top = { x: 0, y: d, z: 0 };
      coords.left = { x: -d * 0.9, y: -d * 0.5, z: 0 };
      coords.right = { x: d * 0.9, y: -d * 0.5, z: d * 0.5 };
      coords.bottom = { x: 0, y: -d * 0.5, z: -d * 0.5 }; // approximate
  }

  Object.entries(diagramData.ligands).forEach(([pos, label]) => {
    if (!coords[pos]) return;
    
    // Parse label (remove charge for element guess)
    let symbol = label.replace(/[0-9+\-]/g, "");
    if (symbol.length > 2) symbol = "X"; // Generic for complex ligands
    
    // For specific knowns
    if (label.includes("Cl")) symbol = "Cl";
    if (label.includes("N")) symbol = "N";
    if (label.includes("O")) symbol = "O";
    if (label.includes("C")) symbol = "C";
    
    const atom = new ChemDoodle.structures.Atom(symbol);
    // Custom label to show full text (e.g. NH3)
    // ChemDoodle atoms usually show element, we might need to set a custom label property if supported or just rely on element
    // Ideally we use label, but ChemDoodle might re-calculate from element. 
    // Let's try setting the element to the label if it's short, or generic 'L' with a tag.
    // Actually, ChemDoodle atoms have a 'label' field for pure text overlay in 2D?
    // We will stick to element symbols for structure and maybe overlay text if possible, 
    // but for now let's just use the inferred element.
    
    atom.x = coords[pos].x;
    atom.y = coords[pos].y;
    atom.z = coords[pos].z;
    
    mol.atoms.push(atom);
    const bond = new ChemDoodle.structures.Bond(centerAtom, atom);
    mol.bonds.push(bond);
  });
  
  return mol;
};

const renderMolecule = (question, diagramData) => {
  if (!viewer2D || !viewer3D) return;
  
  const mol = buildMolecule(diagramData, question.geometry);
  
  // 2D Render
  viewer2D.loadMolecule(mol);
  
  // 3D Render
  // Setup labels
  if (state.showLabels) {
     viewer3D.styles.atoms_displayLabels_3D = true;
  } else {
     viewer3D.styles.atoms_displayLabels_3D = false;
  }
  
  // Color mode
  if (state.colorMode === "charge") {
     // Custom coloring logic would go here, iterating atoms and setting color
     // viewer3D.specs.atoms_color = ...
  }
  
  viewer3D.loadMolecule(mol);
};


// Game Logic
const getQuestionPool = () => {
  if (state.difficulty === "all") return questions;
  return questions.filter((q) => q.difficulty === state.difficulty) || questions;
};

const getSimilarQuestions = (current) => {
  const pool = getQuestionPool();
  const targetTags = new Set(current.tags);
  return pool
    .filter((q) => q !== current)
    .map((q) => ({
      q,
      overlap: q.tags.filter((t) => targetTags.has(t)).length
    }))
    .filter((x) => x.overlap > 0)
    .sort((a, b) => b.overlap - a.overlap)
    .map((x) => x.q);
};

const loadQuestion = () => {
  const pool = getQuestionPool();
  // Simple random for now, or adaptive
  let question;
  if (state.adaptive && state.adaptiveQueue.length) {
    question = state.adaptiveQueue.shift();
  } else {
    // Random from pool not in used if possible
    const available = pool.filter(q => !state.used.has(questions.indexOf(q)));
    const targetPool = available.length ? available : pool;
    if (available.length === 0) state.used.clear();
    
    question = targetPool[Math.floor(Math.random() * targetPool.length)];
  }
  
  state.used.add(questions.indexOf(question));
  state.currentIndex = questions.indexOf(question);
  
  // Update UI
  ui.questionType.textContent = question.type;
  ui.difficultyBadge.textContent = question.difficulty || "Core";
  ui.questionPrompt.textContent = question.formula;
  ui.questionNote.textContent = question.note;
  ui.geometryHint.textContent = question.geometry;
  
  compareState.active = false;
  ui.compareBtn.style.display = question.compare ? "inline-flex" : "none";
  ui.compareLabel.textContent = question.compare ? "Viewing prompt isomer" : "";
  
  ui.answerInput.value = "";
  ui.feedback.className = "feedback";
  ui.feedback.textContent = "";
  ui.answerInput.focus();
  
  const diagramData = question.compare && compareState.active ? question.compare.diagram : question.diagram;
  renderMolecule(question, diagramData);
};

const checkAnswer = () => {
  const q = questions[state.currentIndex];
  const user = normalizeAnswer(ui.answerInput.value);
  if (!user) return;
  
  const correct = q.accepted.some((a) => normalizeAnswer(a) === user);
  
  state.total++;
  if (correct) {
    state.correct++;
    state.streak++;
    // Rigor check
    if (state.rigorMode && !state.labelsLocked && state.streak >= 6 && state.total >= 12 && (state.correct/state.total) >= 0.8) {
      state.labelsLocked = true;
      state.showLabels = false;
      ui.labelToggle.classList.add("locked");
      ui.labelToggle.textContent = "Labels locked";
      saveSettings(settingsKey, state);
      // Re-render to hide labels
      const diagramData = compareState.active && q.compare ? q.compare.diagram : q.diagram;
      renderMolecule(q, diagramData);
    }
  } else {
    state.streak = 0;
    if (state.adaptive) {
      const similars = getSimilarQuestions(q);
      if (similars.length) state.adaptiveQueue.push(similars[0]);
    }
  }
  
  ui.feedback.className = `feedback ${correct ? "success" : "error"}`;
  ui.feedback.textContent = correct 
    ? `Correct. ${q.rationale}` 
    : `Expected: ${q.accepted[0]}. ${q.rationale}`;
    
  updateUI(ui, state);
  setTimeout(loadQuestion, 1500);
};

// Listeners
const setupListeners = () => {
  ui.startBtn.addEventListener("click", () => {
    state.streak = 0; state.correct = 0; state.total = 0; state.used.clear();
    updateUI(ui, state);
    loadQuestion();
  });
  
  ui.submitBtn.addEventListener("click", checkAnswer);
  ui.answerInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") checkAnswer();
  });
  
  ui.skipBtn.addEventListener("click", () => {
    state.total++; state.streak = 0;
    updateUI(ui, state);
    loadQuestion();
  });
  
  ui.compareBtn.addEventListener("click", () => {
    const q = questions[state.currentIndex];
    if (!q.compare) return;
    compareState.active = !compareState.active;
    ui.compareLabel.textContent = compareState.active ? `Viewing ${q.compare.label}` : "Viewing prompt isomer";
    const diagramData = compareState.active ? q.compare.diagram : q.diagram;
    renderMolecule(q, diagramData);
  });
  
  ui.labelToggle.addEventListener("click", () => {
    if (state.labelsLocked) return;
    state.showLabels = !state.showLabels;
    ui.labelToggle.classList.toggle("active", state.showLabels);
    saveSettings(settingsKey, state);
    const q = questions[state.currentIndex];
    const d = compareState.active && q.compare ? q.compare.diagram : q.diagram;
    renderMolecule(q, d);
  });
  
  ui.colorToggle.addEventListener("click", () => {
    state.colorMode = state.colorMode === "donor" ? "charge" : "donor";
    ui.colorToggle.textContent = `Color: ${state.colorMode}`;
    saveSettings(settingsKey, state);
    // Re-render
    const q = questions[state.currentIndex];
    const d = compareState.active && q.compare ? q.compare.diagram : q.diagram;
    renderMolecule(q, d);
  });
  
  ui.rigorToggle.addEventListener("click", () => {
    state.rigorMode = !state.rigorMode;
    ui.rigorToggle.textContent = state.rigorMode ? "On" : "Off";
    ui.rigorToggle.classList.toggle("off", !state.rigorMode);
    if (!state.rigorMode) {
        state.labelsLocked = false;
        ui.labelToggle.classList.remove("locked");
        ui.labelToggle.textContent = "Labels";
    }
    saveSettings(settingsKey, state);
  });
  
  ui.adaptiveToggle.addEventListener("click", () => {
    state.adaptive = !state.adaptive;
    ui.adaptiveToggle.textContent = state.adaptive ? "On" : "Off";
    ui.adaptiveToggle.classList.toggle("off", !state.adaptive);
    saveSettings(settingsKey, state);
  });
  
  ui.difficultyChips.forEach(chip => {
    chip.addEventListener("click", () => {
      state.difficulty = chip.dataset.difficulty;
      ui.difficultyChips.forEach(c => c.classList.toggle("active", c === chip));
      state.used.clear();
      state.adaptiveQueue = [];
      saveSettings(settingsKey, state);
      loadQuestion();
    });
  });
};

init();