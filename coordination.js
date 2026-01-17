import {
  normalizeAnswer,
  loadSettings,
  saveSettings,
  updateUI,
  createElement
} from "./js/utils.js";

// Global State
let questionPools = {};
const state = {
  mode: "match",
  streak: 0,
  correct: 0,
  total: 0,
  used: new Set(),
  adaptiveQueue: [],
  adaptive: true,
  showLabels: true,
  colorMode: "donor",
  rigorMode: false,
  labelsLocked: false,
  currentQuestion: null,
  selections: {},
};

const settingsKey = "coordination-structures-settings";

// Geometry Layouts (Configuration)
const geometryLayouts = {
  octahedral: {
    cn: 6,
    positions: ["top", "bottom", "left", "right", "front", "back"],
    coords: {
      top: [0, 0, 1], bottom: [0, 0, -1], left: [-1, 0, 0],
      right: [1, 0, 0], front: [0, 1, 0], back: [0, -1, 0],
    },
  },
  tetrahedral: {
    cn: 4,
    positions: ["top", "bottom", "left", "right"],
    coords: {
      top: [1, 1, 1], bottom: [-1, -1, 1],
      left: [-1, 1, -1], right: [1, -1, -1],
    },
  },
  "square planar": {
    cn: 4,
    positions: ["top", "bottom", "left", "right"],
    coords: {
      top: [0, 1, 0], bottom: [0, -1, 0],
      left: [-1, 0, 0], right: [1, 0, 0],
    },
  },
  "trigonal bipyramidal": {
    cn: 5,
    positions: ["top", "bottom", "left", "right", "front"],
    coords: {
      top: [0, 0, 1], bottom: [0, 0, -1],
      left: [-1, 0, 0], right: [1, 0, 0], front: [0, 1, 0],
    },
  },
  "square pyramidal": {
    cn: 5,
    positions: ["top", "left", "right", "front", "back"],
    coords: {
      top: [0, 0, 1], left: [-1, 0, 0], right: [1, 0, 0],
      front: [0, 1, 0], back: [0, -1, 0],
    },
  },
  "pentagonal bipyramidal": {
    cn: 7,
    positions: ["top", "bottom", "eq1", "eq2", "eq3", "eq4", "eq5"],
    coords: {
      top: [0, 0, 1], bottom: [0, 0, -1],
      eq1: [1, 0, 0], eq2: [0.309, 0.951, 0], eq3: [-0.809, 0.588, 0],
      eq4: [-0.809, -0.588, 0], eq5: [0.309, -0.951, 0],
    },
  },
  "square antiprismatic": {
    cn: 8,
    positions: ["t1", "t2", "t3", "t4", "b1", "b2", "b3", "b4"],
    coords: {
      t1: [1, 0, 0.8], t2: [0, 1, 0.8], t3: [-1, 0, 0.8], t4: [0, -1, 0.8],
      b1: [0.707, 0.707, -0.8], b2: [-0.707, 0.707, -0.8],
      b3: [-0.707, -0.707, -0.8], b4: [0.707, -0.707, -0.8],
    },
  },
  linear: {
    cn: 2,
    positions: ["left", "right"],
    coords: { left: [-1, 0, 0], right: [1, 0, 0] },
  },
};

const geometryList = Object.keys(geometryLayouts);

// UI Elements
const ui = {
  modeButtons: Array.from(document.querySelectorAll(".mode-tabs .chip")),
  modeBadge: document.getElementById("modeBadge"),
  cnBadge: document.getElementById("cnBadge"),
  geometryBadge: document.getElementById("geometryBadge"),
  promptTitle: document.getElementById("promptTitle"),
  promptNote: document.getElementById("promptNote"),
  answerZone: document.getElementById("answerZone"),
  feedback: document.getElementById("feedback"),
  streak: document.getElementById("streak"),
  accuracy: document.getElementById("accuracy"),
  questionCount: document.getElementById("questionCount"),
  checkBtn: document.getElementById("checkBtn"),
  nextBtn: document.getElementById("nextBtn"),
  resetBtn: document.getElementById("resetBtn"),
  adaptiveToggle: document.getElementById("adaptiveToggle"),
  rigorToggle: document.getElementById("rigorToggle"),
  labelToggle: document.getElementById("labelToggle"),
  colorToggle: document.getElementById("colorToggle"),
  viewerNote: document.getElementById("viewerNote"),
  viewerElement: document.getElementById("viewer3d"),
};

let viewer3D = null;

// Initialization
const init = async () => {
  try {
    const response = await fetch("./data/coordination.json");
    questionPools = await response.json();
    processTags();
    
    const saved = loadSettings(settingsKey, state);
    Object.assign(state, saved);
    
    initChemDoodle();
    setupListeners();
    updateToggleUI();
    updateUI(ui, state);
    loadQuestion();
    
  } catch (error) {
    console.error("Failed to init coordination module:", error);
    ui.promptTitle.textContent = "Error loading content.";
  }
};

const processTags = () => {
  // Add tags for adaptive logic
  Object.keys(questionPools).forEach(key => {
    questionPools[key].forEach(q => {
      const tags = new Set([key, `cn${q.cn}`, q.geometry]);
      if (q.ligands) {
        q.ligands.forEach(l => tags.add(l.split(" ")[0].toLowerCase()));
      }
      q.tags = Array.from(tags);
    });
  });
};

const initChemDoodle = () => {
    if (typeof ChemDoodle === "undefined") {
        ui.viewerNote.textContent = "ChemDoodle library not loaded.";
        return;
    }
    // Replace old 3Dmol viewer
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

// Molecule Builder
const buildMolecule = (question) => {
    const layout = geometryLayouts[question.geometry];
    if (!layout) return null;
    
    const mol = new ChemDoodle.structures.Molecule();
    const metalSym = question.metal || (question.prompt.match(/[A-Z][a-z]?/) || ["M"])[0];
    
    const center = new ChemDoodle.structures.Atom(metalSym);
    center.x = 0; center.y = 0; center.z = 0;
    mol.atoms.push(center);
    
    const ligands = question.ligands || Array(layout.cn).fill("L");
    const scale = 1.5; // Bond length scaling
    
    layout.positions.forEach((pos, idx) => {
        const coord = layout.coords[pos];
        if (!coord) return;
        
        const label = ligands[idx] || "L";
        // Infer element from label
        let elem = "C";
        if (label.startsWith("Cl")) elem = "Cl";
        else if (label.startsWith("N")) elem = "N";
        else if (label.startsWith("O")) elem = "O";
        else if (label.startsWith("P")) elem = "P";
        else if (label.startsWith("F")) elem = "F";
        else if (label.startsWith("Br")) elem = "Br";
        else if (label.startsWith("I")) elem = "I";
        
        const atom = new ChemDoodle.structures.Atom(elem);
        atom.x = coord[0] * scale;
        atom.y = coord[1] * scale;
        atom.z = coord[2] * scale;
        
        mol.atoms.push(atom);
        mol.bonds.push(new ChemDoodle.structures.Bond(center, atom));
    });
    
    return mol;
};

const render3DModel = (question) => {
    if (!viewer3D) return;
    const mol = buildMolecule(question);
    if (!mol) {
        ui.viewerNote.textContent = "Model unavailable.";
        return;
    }
    
    ui.viewerNote.textContent = "Rotate to view geometry.";
    
    // Settings
    if (state.showLabels) viewer3D.styles.atoms_displayLabels_3D = true;
    else viewer3D.styles.atoms_displayLabels_3D = false;
    
    viewer3D.loadMolecule(mol);
};

// Logic
const getPool = () => questionPools[state.mode] || [];

const getNextQuestion = () => {
    const pool = getPool();
    if (state.adaptive && state.adaptiveQueue.length) return state.adaptiveQueue.shift();
    
    // Filter used
    const available = pool.filter(q => !state.used.has(q)); // Weak comparison as objects might be new, but here referentially stable from init
    const target = available.length ? available : pool;
    if (!available.length) state.used.clear();
    
    const pick = target[Math.floor(Math.random() * target.length)];
    state.used.add(pick);
    return pick;
};

const loadQuestion = () => {
    const q = getNextQuestion();
    if (!q) return;
    state.currentQuestion = q;
    state.selections = {};
    
    ui.modeBadge.textContent = state.mode;
    ui.cnBadge.textContent = `CN ${q.cn}`;
    ui.geometryBadge.textContent = q.geometry;
    ui.promptTitle.textContent = q.prompt;
    ui.promptNote.textContent = q.note;
    ui.feedback.textContent = "";
    ui.feedback.className = "feedback";
    
    renderAnswerZone(q);
    render3DModel(q);
};

// UI Rendering
const createOptionButton = (label, group) => {
    const btn = createElement("button", "option-button", label);
    btn.addEventListener("click", () => {
        state.selections[group] = label;
        // Visual toggle
        const siblings = btn.parentElement.querySelectorAll(".option-button");
        siblings.forEach(s => s.classList.remove("active"));
        btn.classList.add("active");
    });
    return btn;
};

const renderAnswerZone = (q) => {
    ui.answerZone.innerHTML = "";
    
    // Helper to add block
    const addBlock = (title, items, group) => {
        const b = createElement("div", "answer-block");
        b.innerHTML = `<h4>${title}</h4>`;
        const g = createElement("div", "option-grid");
        items.forEach(i => g.appendChild(createOptionButton(i, group)));
        b.appendChild(g);
        ui.answerZone.appendChild(b);
    };

    if (state.mode === "match" || state.mode === "build") {
        if (state.mode === "build") {
             const lDiv = createElement("div", "answer-block");
             lDiv.innerHTML = "<h4>Ligands</h4>";
             const list = createElement("div");
             q.ligands.forEach(l => {
                 const chip = createElement("span", "hint-chip", l);
                 list.appendChild(chip);
             });
             lDiv.appendChild(list);
             ui.answerZone.appendChild(lDiv);
        }
        addBlock("Coordination number", ["2", "4", "5", "6", "7", "8"], "cn");
        addBlock("Geometry", geometryList, "geometry");
    } else if (state.mode === "ambiguity") {
        addBlock("Geometry", q.options, "geometry");
        addBlock("Justification", q.justifications, "justification");
    } else if (state.mode === "rare") {
        addBlock("Geometry", ["square pyramidal", "trigonal bipyramidal", "pentagonal bipyramidal", "square antiprismatic"], "geometry");
    }
};

const markOptions = (group, correctValue) => {
    const btns = ui.answerZone.querySelectorAll(".option-button");
    btns.forEach(btn => {
        // Simple heuristic: check parent header?
        // Actually better: check click handler group... but we can't inspect listeners.
        // We will assume unique values or context.
        // Or simply iterate selections if we stored element refs.
        // For now, let's just highlight correct text if it matches selection group context
        // This is a bit tricky without structured DOM mapping.
        // Let's iterate blocks.
    });
    // Simplified feedback: Just show text result.
};

const checkAnswer = () => {
    const q = state.currentQuestion;
    if (!q) return;
    
    let isCorrect = false;
    let expected = "";
    
    if (state.mode === "ambiguity") {
        isCorrect = normalizeAnswer(state.selections.geometry || "") === q.geometry &&
                    normalizeAnswer(state.selections.justification || "") === normalizeAnswer(q.justification);
        expected = `${q.geometry} because ${q.justification}`;
    } else if (state.mode === "rare") {
        isCorrect = normalizeAnswer(state.selections.geometry || "") === q.geometry;
        expected = q.geometry;
    } else {
        isCorrect = Number(state.selections.cn) === q.cn &&
                    normalizeAnswer(state.selections.geometry || "") === q.geometry;
        expected = `CN ${q.cn}, ${q.geometry}`;
    }
    
    state.total++;
    if(isCorrect) { state.correct++; state.streak++; checkMastery(); }
    else { state.streak = 0; enqueueAdaptive(q); }
    
    ui.feedback.className = `feedback ${isCorrect ? "success" : "error"}`;
    ui.feedback.textContent = isCorrect ? "Correct." : `Expected: ${expected}`;
    updateUI(ui, state);
};

const checkMastery = () => {
    if (!state.rigorMode || state.labelsLocked) return;
    if (state.total >= 12 && (state.correct/state.total) >= 0.8 && state.streak >= 6) {
        state.labelsLocked = true;
        state.showLabels = false;
        updateToggleUI();
        saveSettings(settingsKey, state);
        render3DModel(state.currentQuestion);
    }
};

const enqueueAdaptive = (q) => {
    if (!state.adaptive) return;
    const pool = getPool();
    const tags = new Set(q.tags);
    // Find similar
    const best = pool.filter(c => c !== q)
                     .map(c => ({ c, score: (c.tags||[]).filter(t => tags.has(t)).length }))
                     .sort((a,b) => b.score - a.score)[0];
    if (best && best.score > 0) state.adaptiveQueue.push(best.c);
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
    ui.resetBtn.addEventListener("click", () => {
        state.streak = 0; state.correct = 0; state.total = 0;
        state.used.clear(); state.adaptiveQueue = [];
        updateUI(ui, state); loadQuestion();
    });
    
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
};

init();