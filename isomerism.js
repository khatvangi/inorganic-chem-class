import {
  normalizeAnswer,
  loadSettings,
  saveSettings,
  updateUI,
  createElement
} from "./js/utils.js";

// Global State
let questionData = {};
const state = {
  mode: "geometric",
  streak: 0,
  correct: 0,
  total: 0,
  adaptive: true,
  adaptiveQueue: [],
  showLabels: true,
  colorMode: "donor",
  rigorMode: false,
  labelsLocked: false,
  currentQuestion: null,
  selection: null,
  compareActive: false,
  mirrorMode: false,
};

const settingsKey = "coordination-isomerism-settings";

// Geometry Layouts (Simplified for Isomerism)
const geometryLayouts = {
  octahedral: {
    positions: ["top", "bottom", "left", "right", "front", "back"],
    coords: {
      top: [0, 0, 1], bottom: [0, 0, -1], left: [-1, 0, 0],
      right: [1, 0, 0], front: [0, 1, 0], back: [0, -1, 0],
    },
  },
  "square planar": {
    positions: ["top", "bottom", "left", "right"],
    coords: {
      top: [0, 1, 0], bottom: [0, -1, 0],
      left: [-1, 0, 0], right: [1, 0, 0],
    },
  },
};

// UI Elements
const ui = {
  modeButtons: Array.from(document.querySelectorAll(".mode-tabs .chip")),
  modeBadge: document.getElementById("modeBadge"),
  topicBadge: document.getElementById("topicBadge"),
  promptTitle: document.getElementById("promptTitle"),
  promptNote: document.getElementById("promptNote"),
  answerZone: document.getElementById("answerZone"),
  feedback: document.getElementById("feedback"),
  streak: document.getElementById("streak"),
  accuracy: document.getElementById("accuracy"),
  questionCount: document.getElementById("questionCount"),
  checkBtn: document.getElementById("checkBtn"),
  nextBtn: document.getElementById("nextBtn"),
  adaptiveToggle: document.getElementById("adaptiveToggle"),
  rigorToggle: document.getElementById("rigorToggle"),
  labelToggle: document.getElementById("labelToggle"),
  colorToggle: document.getElementById("colorToggle"),
  compareBtn: document.getElementById("compareBtn"),
  mirrorBtn: document.getElementById("mirrorBtn"),
  viewerNote: document.getElementById("viewerNote"),
  viewerElement: document.getElementById("viewer3d"),
};

let viewer3D = null;

// Initialization
const init = async () => {
  try {
    const response = await fetch("./data/isomerism.json");
    questionData = await response.json();
    
    const saved = loadSettings(settingsKey, state);
    Object.assign(state, saved);
    
    initChemDoodle();
    setupListeners();
    updateToggleUI();
    updateUI(ui, state);
    loadQuestion();
  } catch (error) {
    console.error("Failed to init isomerism module:", error);
    ui.promptTitle.textContent = "Error loading content.";
  }
};

const initChemDoodle = () => {
    if (typeof ChemDoodle === "undefined") {
        ui.viewerNote.textContent = "ChemDoodle library not loaded.";
        return;
    }
    ui.viewerElement.innerHTML = "";
    const canvas = document.createElement("canvas");
    canvas.id = "chemDoodle3D";
    canvas.width = 300;
    canvas.height = 300;
    ui.viewerElement.appendChild(canvas);
    
    viewer3D = new ChemDoodle.ViewerCanvas3D("chemDoodle3D", 300, 300);
    viewer3D.styles.backgroundColor = "white";
    viewer3D.styles.atoms_useJMOLColors = true;
    viewer3D.styles.bonds_color = "black";
    viewer3D.styles.atoms_sphereDiameter_3D = 0.6;
};

// Logic
const getPool = () => questionData[state.mode] || [];

const getNextQuestion = () => {
    const pool = getPool();
    if (state.adaptive && state.adaptiveQueue.length) return state.adaptiveQueue.shift();
    
    // Simple random
    return pool[Math.floor(Math.random() * pool.length)];
};

const loadQuestion = () => {
    const q = getNextQuestion();
    state.currentQuestion = q;
    state.selection = null;
    state.compareActive = false;
    state.mirrorMode = false;
    
    ui.modeBadge.textContent = state.mode.charAt(0).toUpperCase() + state.mode.slice(1);
    ui.topicBadge.textContent = q.topic || q.answer;
    ui.promptTitle.textContent = q.formula || "Classification";
    ui.promptNote.innerHTML = (q.prompt || "").replace(/\n/g, "<br>");
    
    ui.feedback.textContent = "";
    ui.feedback.className = "feedback";
    
    renderOptions(q);
    
    ui.compareBtn.style.display = (state.mode === "structural" || !q.compare) ? "none" : "inline-flex";
    ui.compareBtn.textContent = state.mode === "optical" ? "Compare enantiomer" : "Compare isomer";
    
    updateToggleUI();
    render3DModel(q);
};

const renderOptions = (q) => {
    ui.answerZone.innerHTML = "";
    const block = createElement("div", "answer-block");
    block.innerHTML = "<h4>Select classification</h4>";
    const grid = createElement("div", "option-grid");
    
    let options = [];
    if (state.mode === "geometric") options = q.topic === "fac/mer" ? ["fac", "mer"] : ["cis", "trans"];
    else if (state.mode === "optical") options = ["lambda", "delta"];
    else options = q.options;
    
    options.forEach(opt => {
        const btn = createElement("button", "option-button", opt);
        btn.addEventListener("click", () => {
            state.selection = opt;
            const siblings = grid.querySelectorAll(".option-button");
            siblings.forEach(s => s.classList.remove("active"));
            btn.classList.add("active");
        });
        grid.appendChild(btn);
    });
    
    block.appendChild(grid);
    ui.answerZone.appendChild(block);
};

// 3D Rendering
const render3DModel = (q) => {
    if (!viewer3D) return;
    viewer3D.emptyContent();
    
    if (state.mode === "structural") {
        ui.viewerNote.textContent = "No 3D model for structural isomers.";
        viewer3D.repaint();
        return;
    }
    
    const mol = new ChemDoodle.structures.Molecule();
    
    if (state.mode === "optical") {
        ui.viewerNote.textContent = state.mirrorMode ? "Mirror view enabled." : "Rotate to observe helicity.";
        const modelKey = state.compareActive ? q.compare : q.model;
        const modelData = questionData.models[modelKey];
        if (!modelData) return;
        
        // Central
        const central = new ChemDoodle.structures.Atom(modelData.central || "Co");
        central.x = 0; central.y = 0; central.z = 0;
        mol.atoms.push(central);
        
        modelData.atoms.forEach(a => {
            const atom = new ChemDoodle.structures.Atom(a.element || "N");
            atom.x = state.mirrorMode ? -a.x : a.x;
            atom.y = a.y;
            atom.z = a.z;
            mol.atoms.push(atom);
            mol.bonds.push(new ChemDoodle.structures.Bond(central, atom));
        });
    } else {
        // Geometric
        ui.viewerNote.textContent = "Rotate to inspect positions.";
        const diagram = state.compareActive && q.compare ? q.compare.diagram : q.diagram;
        const layout = geometryLayouts[q.geometry];
        if (!layout) return;
        
        // Central
        const centerSym = (diagram.central || "M").replace(/[^A-Za-z]/g, "");
        const central = new ChemDoodle.structures.Atom(centerSym);
        mol.atoms.push(central);
        
        const scale = 1.5;
        layout.positions.forEach(pos => {
            if (!diagram.ligands[pos] || !layout.coords[pos]) return;
            const label = diagram.ligands[pos];
            // Element inference
            let elem = "C";
            if(label.includes("Cl")) elem = "Cl";
            else if(label.includes("N")) elem = "N";
            
            const atom = new ChemDoodle.structures.Atom(elem);
            const c = layout.coords[pos];
            atom.x = c[0] * scale;
            atom.y = c[1] * scale;
            atom.z = c[2] * scale;
            mol.atoms.push(atom);
            mol.bonds.push(new ChemDoodle.structures.Bond(central, atom));
        });
    }
    
    // Labels
    if (state.showLabels) viewer3D.styles.atoms_displayLabels_3D = true;
    else viewer3D.styles.atoms_displayLabels_3D = false;
    
    viewer3D.loadMolecule(mol);
};

const checkAnswer = () => {
    const q = state.currentQuestion;
    if (!q || !state.selection) return;
    
    const isCorrect = state.selection.toLowerCase() === q.answer.toLowerCase();
    
    state.total++;
    if (isCorrect) { state.correct++; state.streak++; checkMastery(); } 
    else { state.streak = 0; enqueueAdaptive(q); }
    
    ui.feedback.className = `feedback ${isCorrect ? "success" : "error"}`;
    ui.feedback.textContent = isCorrect ? "Correct." : `Expected: ${q.answer}`;
    updateUI(ui, state);
};

const checkMastery = () => {
    if (!state.rigorMode || state.labelsLocked) return;
    if (state.total >= 10 && (state.correct/state.total) >= 0.8 && state.streak >= 5) {
        state.labelsLocked = true;
        state.showLabels = false;
        updateToggleUI();
        saveSettings(settingsKey, state);
        render3DModel(state.currentQuestion);
    }
};

const enqueueAdaptive = (q) => {
    if (!state.adaptive) return;
    // Simple push back similar logic
    const pool = getPool();
    const similar = pool.find(i => i.id !== q.id && i.topic === q.topic);
    if(similar) state.adaptiveQueue.push(similar);
};

// Listeners
const setupListeners = () => {
    ui.modeButtons.forEach(btn => {
        btn.addEventListener("click", () => {
            ui.modeButtons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            state.mode = btn.dataset.mode;
            state.adaptiveQueue = [];
            loadQuestion();
        });
    });
    
    ui.checkBtn.addEventListener("click", checkAnswer);
    ui.nextBtn.addEventListener("click", loadQuestion);
    
    ui.adaptiveToggle.addEventListener("click", () => {
        state.adaptive = !state.adaptive;
        updateToggleUI(); saveSettings(settingsKey, state);
    });
    
    ui.rigorToggle.addEventListener("click", () => {
        state.rigorMode = !state.rigorMode;
        if(!state.rigorMode) { state.labelsLocked = false; state.showLabels = true; }
        else checkMastery();
        updateToggleUI(); saveSettings(settingsKey, state);
        render3DModel(state.currentQuestion);
    });
    
    ui.labelToggle.addEventListener("click", () => {
        if(state.labelsLocked) return;
        state.showLabels = !state.showLabels;
        updateToggleUI(); saveSettings(settingsKey, state);
        render3DModel(state.currentQuestion);
    });
    
    ui.colorToggle.addEventListener("click", () => {
        state.colorMode = state.colorMode === "donor" ? "charge" : "donor";
        ui.colorToggle.textContent = `Color: ${state.colorMode}`;
        saveSettings(settingsKey, state);
        render3DModel(state.currentQuestion);
    });
    
    ui.compareBtn.addEventListener("click", () => {
        state.compareActive = !state.compareActive;
        render3DModel(state.currentQuestion);
    });
    
    ui.mirrorBtn.addEventListener("click", () => {
        state.mirrorMode = !state.mirrorMode;
        render3DModel(state.currentQuestion);
    });
};

const updateToggleUI = () => {
    ui.adaptiveToggle.textContent = state.adaptive ? "On" : "Off";
    ui.adaptiveToggle.classList.toggle("off", !state.adaptive);
    ui.rigorToggle.textContent = state.rigorMode ? "On" : "Off";
    ui.rigorToggle.classList.toggle("off", !state.rigorMode);
    
    if (state.labelsLocked) {
        ui.labelToggle.textContent = "Locked";
        ui.labelToggle.classList.add("off");
        ui.labelToggle.disabled = true;
    } else {
        ui.labelToggle.textContent = state.showLabels ? "On" : "Off";
        ui.labelToggle.classList.toggle("off", !state.showLabels);
        ui.labelToggle.disabled = false;
    }
    
    ui.mirrorBtn.style.display = state.mode === "optical" ? "inline-flex" : "none";
};

init();