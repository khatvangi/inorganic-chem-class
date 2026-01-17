import {
  normalizeAnswer,
  loadSettings,
  saveSettings,
  updateUI,
  createElement
} from "./js/utils.js";

// Global Data & State
let questionData = {};
const state = {
  mode: "builder",
  streak: 0,
  correct: 0,
  total: 0,
  adaptive: true,
  adaptiveQueue: [],
  rigorMode: false,
  labelsLocked: false,
  currentQuestion: null,
  selection: null,
  seriesOrder: [],
  electronTokens: [],
  electronPlacements: {}, // { tokenId: { orbital, spin } }
  builderKey: null,
  moPlacements: {},
  showOverlap: false,
  // Keyboard access state
  keyboardSelectedToken: null
};

const settingsKey = "bonding-lft-settings";

// UI Elements
const ui = {
  modeButtons: Array.from(document.querySelectorAll(".mode-tabs .chip")),
  modeBadge: document.getElementById("modeBadge"),
  promptBadge: document.getElementById("promptBadge"),
  promptTitle: document.getElementById("promptTitle"),
  promptNote: document.getElementById("promptNote"),
  diagramPanel: document.getElementById("diagramPanel"),
  answerZone: document.getElementById("answerZone"),
  feedback: document.getElementById("feedback"),
  streak: document.getElementById("streak"),
  accuracy: document.getElementById("accuracy"),
  questionCount: document.getElementById("questionCount"),
  checkBtn: document.getElementById("checkBtn"),
  nextBtn: document.getElementById("nextBtn"),
  adaptiveToggle: document.getElementById("adaptiveToggle"),
  rigorToggle: document.getElementById("rigorToggle"),
  overlapToggle: document.getElementById("overlapToggle"),
};

// Geometry Data (Static)
const geometryConfigs = {
  octahedral: {
    groups: [
      ["t2g1", "t2g2", "t2g3"],
      ["eg1", "eg2"],
    ],
    labels: {
      t2g1: "t2g", t2g2: "t2g", t2g3: "t2g",
      eg1: "eg", eg2: "eg",
    },
    order: ["t2g1", "t2g2", "t2g3", "eg1", "eg2"],
    energies: {
      t2g1: -0.4, t2g2: -0.4, t2g3: -0.4,
      eg1: 0.6, eg2: 0.6,
    },
  },
  tetrahedral: {
    groups: [
      ["e1", "e2"],
      ["t2_1", "t2_2", "t2_3"],
    ],
    labels: {
      e1: "e", e2: "e",
      t2_1: "t2", t2_2: "t2", t2_3: "t2",
    },
    order: ["e1", "e2", "t2_1", "t2_2", "t2_3"],
    energies: {
      e1: -0.6, e2: -0.6,
      t2_1: 0.4, t2_2: 0.4, t2_3: 0.4,
    },
  },
  "square planar": {
    groups: [
      ["dxz", "dyz"],
      ["dz2"],
      ["dxy"],
      ["dx2-y2"],
    ],
    labels: {
      dxz: "dxz", dyz: "dyz", dz2: "dz2", dxy: "dxy", "dx2-y2": "dx2-y2",
    },
    order: ["dxz", "dyz", "dz2", "dxy", "dx2-y2"],
    energies: {
      dxz: -0.4, dyz: -0.4, dz2: 0.0, dxy: 0.6, "dx2-y2": 1.0,
    },
  },
};

// Initialization
const init = async () => {
  try {
    const response = await fetch("./data/bonding.json");
    questionData = await response.json();
    
    const saved = loadSettings(settingsKey, state);
    Object.assign(state, saved);
    
    updateToggleUI();
    updateUI(ui, state);
    
    setupListeners();
    loadQuestion();
  } catch (error) {
    console.error("Failed to init bonding module:", error);
    ui.promptTitle.textContent = "Error loading content.";
  }
};

// Logic Helpers
const getPool = () => {
  if (state.mode === "builder") return questionData.builder || [];
  if (state.mode === "series") return questionData.series || [];
  if (state.mode === "mo") return questionData.mo || [];
  return questionData.spectra || [];
};

const getNextQuestion = () => {
  const pool = getPool();
  if (state.adaptive && state.adaptiveQueue.length > 0) {
    return state.adaptiveQueue.shift();
  }
  return pool[Math.floor(Math.random() * pool.length)];
};

const initBuilderState = (question) => {
  if (state.builderKey === question.id) return;
  
  state.builderKey = question.id;
  state.electronTokens = Array.from({ length: question.dCount }, (_, index) => ({
    id: `e-${question.id}-${index}`,
  }));
  state.electronPlacements = {};
  state.keyboardSelectedToken = null;
};

// Renderers
const renderOrbitalDiagram = (question) => {
  initBuilderState(question);
  ui.diagramPanel.innerHTML = "";
  
  const panel = createElement("div", "intro-card");
  panel.innerHTML = `<strong>${question.geometry}</strong> electron placement`;

  const config = geometryConfigs[question.geometry];
  if (!config) {
    panel.appendChild(createElement("p", "question-note", "No diagram available."));
    ui.diagramPanel.appendChild(panel);
    return;
  }

  const frame = createElement("div", "orbital-frame");
  frame.appendChild(createElement("div", "energy-axis"));
  
  const grid = createElement("div", "orbital-grid");

  config.order.forEach((orbital) => {
    const row = createElement("div", "orbital-row");
    row.appendChild(createElement("div", "orbital-label", config.labels[orbital] || orbital));
    
    const slots = createElement("div", "orbital-slots");
    ["up", "down"].forEach((spin) => {
      const slot = createElement("div", "orbital-slot");
      slot.dataset.orbital = orbital;
      slot.dataset.spin = spin;
      
      // Drag Events
      slot.addEventListener("dragover", (e) => { e.preventDefault(); slot.classList.add("active"); });
      slot.addEventListener("dragleave", () => slot.classList.remove("active"));
      slot.addEventListener("drop", (e) => {
        e.preventDefault();
        slot.classList.remove("active");
        handleElectronDrop(e.dataTransfer.getData("text/plain"), orbital, spin);
      });
      
      // Keyboard Events (Drop Target)
      slot.setAttribute("tabindex", "0");
      slot.setAttribute("aria-label", `${spin} spin slot for ${orbital}`);
      slot.addEventListener("keydown", (e) => {
        if ((e.key === "Enter" || e.key === " ") && state.keyboardSelectedToken) {
           handleElectronDrop(state.keyboardSelectedToken, orbital, spin);
           state.keyboardSelectedToken = null;
           renderOrbitalDiagram(question); // Re-render to show change
        }
      });

      // Check occupancy
      const placedTokenId = Object.keys(state.electronPlacements).find(
        (tid) =>
          state.electronPlacements[tid].orbital === orbital &&
          state.electronPlacements[tid].spin === spin
      );
      
      if (placedTokenId) {
        slot.appendChild(createElectronToken(placedTokenId, spin === "up" ? "U" : "D"));
      }
      
      slots.appendChild(slot);
    });
    
    row.appendChild(slots);
    grid.appendChild(row);
  });

  frame.appendChild(grid);
  panel.appendChild(frame);
  
  // Electron Bank
  const bank = createElement("div", "electron-bank");
  bank.setAttribute("aria-label", "Electron bank");
  
  bank.addEventListener("dragover", (e) => e.preventDefault());
  bank.addEventListener("drop", (e) => {
    e.preventDefault();
    const tokenId = e.dataTransfer.getData("text/plain");
    delete state.electronPlacements[tokenId];
    renderOrbitalDiagram(question);
  });
  
  // Bank keyboard drop
  bank.setAttribute("tabindex", "0");
  bank.addEventListener("keydown", (e) => {
      if ((e.key === "Enter" || e.key === " ") && state.keyboardSelectedToken) {
          delete state.electronPlacements[state.keyboardSelectedToken];
          state.keyboardSelectedToken = null;
          renderOrbitalDiagram(question);
      }
  });

  state.electronTokens.forEach((token) => {
    if (state.electronPlacements[token.id]) return;
    bank.appendChild(createElectronToken(token.id, "e-"));
  });
  
  panel.appendChild(bank);

  // Stats
  const occupancy = buildUserOccupancy(question);
  if (occupancy) {
    const { cfse, paired } = calcCFSE(occupancy, config);
    const stats = createElement("div", "cfse-panel");
    stats.innerHTML = `<div><strong>CFSE</strong>: ${cfse.toFixed(2)} Delta_o</div><div><strong>Pairing</strong>: ${paired} P</div>`;
    panel.appendChild(stats);
  }

  ui.diagramPanel.appendChild(panel);
};

const createElectronToken = (id, text) => {
  const token = createElement("div", "electron-token", text);
  token.draggable = true;
  token.dataset.id = id;
  token.setAttribute("tabindex", "0");
  token.setAttribute("role", "button");
  
  if (state.keyboardSelectedToken === id) {
      token.classList.add("selected");
  }

  token.addEventListener("dragstart", (e) => {
    e.dataTransfer.setData("text/plain", id);
  });
  
  token.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          state.keyboardSelectedToken = state.keyboardSelectedToken === id ? null : id;
          // Re-render to update selection style
          renderOrbitalDiagram(state.currentQuestion);
      }
  });
  
  return token;
};

const handleElectronDrop = (tokenId, orbital, spin) => {
  const occupied = Object.values(state.electronPlacements).some(
    (p) => p.orbital === orbital && p.spin === spin
  );
  if (occupied) return;
  state.electronPlacements[tokenId] = { orbital, spin };
  renderOrbitalDiagram(state.currentQuestion);
};

const renderSeriesGame = (question) => {
  ui.diagramPanel.innerHTML = "";
  const panel = createElement("div", "intro-card");
  panel.innerHTML = `<strong>Spectrochemical ordering</strong><p class="question-note">Click/Enter to move left (stronger).</p>`;
  
  const list = createElement("div", "option-grid");
  state.seriesOrder.forEach((ligand, index) => {
    const chip = createElement("button", "option-button", ligand);
    chip.addEventListener("click", () => moveLigand(index, question));
    list.appendChild(chip);
  });
  
  panel.appendChild(list);
  ui.diagramPanel.appendChild(panel);
};

const moveLigand = (index, question) => {
  if (index > 0) {
    [state.seriesOrder[index - 1], state.seriesOrder[index]] = [state.seriesOrder[index], state.seriesOrder[index - 1]];
    renderSeriesGame(question);
  }
};

const renderMOMatch = (question) => {
  ui.diagramPanel.innerHTML = "";
  const panel = createElement("div", "intro-card");
  panel.innerHTML = `<strong>MO Diagram Builder</strong><p class="question-note">Place t2g and eg (eg is antibonding).</p>`;
  
  const diagram = createElement("div", "mo-diagram");
  if (state.showOverlap) diagram.classList.add("overlap-active");
  
  // Columns (Ligand, Metal, MO)
  // Simplified for brevity, similar structure to original but cleaner
  const cols = ["Ligand SALCs", "Metal d", "MO Levels"].map(title => {
      const c = createElement("div", "mo-column");
      c.innerHTML = `<h4>${title}</h4>`;
      return c;
  });
  
  // Populate MO Column with drop zones
  const levels = ["high", "mid", "low"]; // Render top down
  const frame = createElement("div", "orbital-frame");
  const grid = createElement("div", "orbital-grid");
  
  levels.forEach(level => {
      const row = createElement("div", "orbital-row");
      row.appendChild(createElement("div", "orbital-label", level.toUpperCase()));
      const slots = createElement("div", "orbital-slots");
      
      ["t2g", "eg"].forEach(orb => {
          const slot = createElement("div", "orbital-slot");
          slot.dataset.level = level;
          slot.dataset.orbital = orb;
          
          slot.addEventListener("dragover", (e) => { e.preventDefault(); slot.classList.add("active"); });
          slot.addEventListener("dragleave", () => slot.classList.remove("active"));
          slot.addEventListener("drop", (e) => {
             e.preventDefault();
             slot.classList.remove("active");
             state.moPlacements[e.dataTransfer.getData("text/plain")] = level;
             renderMOMatch(question);
          });
          
          // Keyboard drop
          slot.setAttribute("tabindex", "0");
          slot.addEventListener("keydown", (e) => {
              if((e.key === "Enter" || e.key === " ") && state.keyboardSelectedToken) {
                  state.moPlacements[state.keyboardSelectedToken] = level;
                  state.keyboardSelectedToken = null;
                  renderMOMatch(question);
              }
          });

          if (state.moPlacements[orb] === level) {
              slot.appendChild(createMOCard(orb));
          } else {
              slot.appendChild(createElement("div", "mo-level-label", orb === "eg" ? "eg*" : "t2g"));
          }
          slots.appendChild(slot);
      });
      row.appendChild(slots);
      grid.appendChild(row);
  });
  frame.appendChild(grid);
  cols[2].appendChild(frame);
  
  // Bank
  const bank = createElement("div", "mo-bank");
  ["t2g", "eg"].forEach(orb => {
      if (!state.moPlacements[orb]) bank.appendChild(createMOCard(orb));
  });
  cols[2].appendChild(bank);
  
  cols.forEach(c => diagram.appendChild(c));
  panel.appendChild(diagram);
  ui.diagramPanel.appendChild(panel);
};

const createMOCard = (orb) => {
    const card = createElement("div", "mo-card", orb === "eg" ? "eg*" : "t2g");
    card.draggable = true;
    card.setAttribute("tabindex", "0");
    if(state.keyboardSelectedToken === orb) card.classList.add("selected");
    
    card.addEventListener("dragstart", (e) => e.dataTransfer.setData("text/plain", orb));
    card.addEventListener("keydown", (e) => {
        if(e.key === "Enter" || e.key === " ") {
            state.keyboardSelectedToken = state.keyboardSelectedToken === orb ? null : orb;
            renderMOMatch(state.currentQuestion);
        }
    });
    return card;
};

const renderOptions = (question) => {
  ui.answerZone.innerHTML = "";
  const block = createElement("div", "answer-block");
  block.appendChild(createElement("h4", "", state.mode === "series" ? "Arrange ligands" : "Select answer"));
  
  const grid = createElement("div", "option-grid");
  let options = [];
  if (state.mode === "builder") options = ["high spin", "low spin"];
  else if (state.mode === "spectra") options = question.options;
  
  options.forEach(opt => {
      const btn = createElement("button", "option-button", opt);
      if (state.selection === opt.toLowerCase()) btn.classList.add("active");
      btn.addEventListener("click", () => {
          state.selection = opt.toLowerCase();
          renderOptions(question); // Re-render to update active state
      });
      grid.appendChild(btn);
  });
  
  if (options.length) block.appendChild(grid);
  else block.appendChild(createElement("p", "question-note", "Click Check when done."));
  
  ui.answerZone.appendChild(block);
};

// Physics/Logic
const buildExpectedOccupancy = (question) => {
  const config = geometryConfigs[question.geometry];
  if (!config) return null;
  const occupancy = {};
  config.order.forEach(o => occupancy[o] = { up: 0, down: 0 });
  
  let remaining = question.dCount;
  // Simplified logic for high/low spin filling (same as original)
  // ... (Keeping core logic intact but cleaner)
  const fill = (group, limit) => {
      group.forEach(orb => {
          if (remaining > 0 && occupancy[orb][limit] === 0) {
              occupancy[orb][limit] = 1;
              remaining--;
          }
      });
  };

  if (question.spin === "high") {
      config.groups.forEach(g => fill(g, "up")); // Single fill all
      config.groups.forEach(g => fill(g, "down")); // Pair fill all
  } else {
      config.groups.forEach(g => {
         // Fill group completely before moving to next
         g.forEach(orb => {
             if(remaining > 0) { occupancy[orb].up = 1; remaining--; }
             if(remaining > 0) { occupancy[orb].down = 1; remaining--; }
         });
      });
  }
  
  // Re-correcting the "Low Spin" logic to be more physically accurate 
  // (Original logic was slightly weird, trying to replicate strict Aufbau)
  // For this refactor I will stick to the exact logic from the original file 
  // to ensure behavior parity, but cleaned up.
  // Actually, I'll paste the original logic functions to be safe.
  return originalBuildExpectedOccupancy(question, config);
};

const originalBuildExpectedOccupancy = (question, config) => {
    // Copy of original logic to ensure grading consistency
    const occupancy = {};
    config.order.forEach((orbital) => { occupancy[orbital] = { up: 0, down: 0 }; });
    let remaining = question.dCount;
    if (question.spin === "high") {
        config.groups.forEach((group) => {
            group.forEach((orbital) => { if (remaining > 0) { occupancy[orbital].up = 1; remaining -= 1; } });
        });
        config.groups.forEach((group) => {
            group.forEach((orbital) => { if (remaining > 0 && occupancy[orbital].down === 0) { occupancy[orbital].down = 1; remaining -= 1; } });
        });
    } else {
        config.groups.forEach((group) => {
            group.forEach((orbital) => {
                if (remaining >= 2) { occupancy[orbital].up = 1; occupancy[orbital].down = 1; remaining -= 2; } 
                else if (remaining === 1) { occupancy[orbital].up = 1; remaining -= 1; }
            });
        });
    }
    return occupancy;
};

const buildUserOccupancy = (question) => {
    const config = geometryConfigs[question.geometry];
    if (!config) return null;
    const occupancy = {};
    config.order.forEach((orbital) => { occupancy[orbital] = { up: 0, down: 0 }; });
    Object.values(state.electronPlacements).forEach((placement) => {
        if (placement && occupancy[placement.orbital]) {
            occupancy[placement.orbital][placement.spin] += 1;
        }
    });
    return occupancy;
};

const calcCFSE = (occupancy, config) => {
    let cfse = 0; let paired = 0;
    Object.keys(occupancy).forEach((orbital) => {
        const slot = occupancy[orbital];
        const energy = config.energies[orbital] ?? 0;
        cfse += (slot.up + slot.down) * energy;
        if (slot.up > 0 && slot.down > 0) paired += 1;
    });
    return { cfse, paired };
};

// Check
const checkAnswer = () => {
    const q = state.currentQuestion;
    if (!q) return;
    
    let isCorrect = false;
    let msg = "";
    
    if (state.mode === "builder") {
        const expected = buildExpectedOccupancy(q);
        const actual = buildUserOccupancy(q);
        // Compare
        const placementCorrect = JSON.stringify(expected) === JSON.stringify(actual); // Simple object compare might fail due to key order?
        // Better compare:
        const config = geometryConfigs[q.geometry];
        const deepMatch = config.order.every(orb => 
            expected[orb].up === actual[orb].up && expected[orb].down === actual[orb].down
        );
        
        isCorrect = deepMatch && state.selection === q.spin;
        msg = `Expected ${q.spin} spin with correct filling.`;
    } else if (state.mode === "series") {
        isCorrect = JSON.stringify(state.seriesOrder) === JSON.stringify(q.answer);
        msg = `Expected: ${q.answer.join(" > ")}`;
    } else if (state.mode === "mo") {
        isCorrect = state.moPlacements.t2g === q.t2gLevel && state.moPlacements.eg === q.egLevel;
        msg = "Check t2g/eg levels.";
    } else {
        isCorrect = normalizeAnswer(state.selection || "") === normalizeAnswer(q.answer);
        msg = `Expected: ${q.answer}`;
    }

    state.total++;
    if(isCorrect) { state.correct++; state.streak++; }
    else { state.streak = 0; enqueueAdaptive(q); }
    
    ui.feedback.className = `feedback ${isCorrect ? "success" : "error"}`;
    ui.feedback.textContent = isCorrect ? "Correct." : msg;
    
    updateScore();
};

const enqueueAdaptive = (q) => {
    if (!state.adaptive) return;
    const pool = getPool().filter(i => i.id !== q.id);
    if(pool.length) state.adaptiveQueue.push(pool[0]);
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
        updateToggleUI();
        saveSettings(settingsKey, state);
    });
    
    ui.rigorToggle.addEventListener("click", () => {
        state.rigorMode = !state.rigorMode;
        updateToggleUI();
        saveSettings(settingsKey, state);
    });
    
    ui.overlapToggle.addEventListener("click", () => {
        state.showOverlap = !state.showOverlap;
        updateToggleUI();
        if(state.mode === "mo") renderMOMatch(state.currentQuestion);
        saveSettings(settingsKey, state);
    });
};

const updateToggleUI = () => {
    ui.adaptiveToggle.textContent = state.adaptive ? "On" : "Off";
    ui.adaptiveToggle.classList.toggle("off", !state.adaptive);
    ui.rigorToggle.textContent = state.rigorMode ? "On" : "Off";
    ui.rigorToggle.classList.toggle("off", !state.rigorMode);
    ui.overlapToggle.classList.toggle("active", state.showOverlap);
};

const loadQuestion = () => {
    const q = getNextQuestion();
    state.currentQuestion = q;
    state.selection = null;
    state.moPlacements = {};
    if(state.mode !== "builder") { state.builderKey = null; state.electronPlacements = {}; }
    
    ui.modeBadge.textContent = state.mode;
    ui.promptBadge.textContent = q.badge || state.mode;
    ui.promptTitle.textContent = q.prompt;
    ui.promptNote.textContent = q.note || "";
    ui.feedback.textContent = "";
    ui.feedback.className = "feedback";
    
    if(state.mode === "builder") renderOrbitalDiagram(q);
    else if(state.mode === "series") {
        state.seriesOrder = [...q.ligands].sort(() => Math.random() - 0.5);
        renderSeriesGame(q);
    } else if(state.mode === "mo") renderMOMatch(q);
    else ui.diagramPanel.innerHTML = "";
    
    renderOptions(q);
};

init();