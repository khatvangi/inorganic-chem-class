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
  mode: "identify",
  streak: 0,
  correct: 0,
  total: 0,
  adaptive: true,
  adaptiveQueue: [],
  rigorMode: false,
  currentQuestion: null,
  selection: null,
};

const settingsKey = "solid-state-settings";

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
};

// Initialization
const init = async () => {
  try {
    const response = await fetch("./data/solids.json");
    questionData = await response.json();
    
    const saved = loadSettings(settingsKey, state);
    Object.assign(state, saved);
    
    updateToggleUI();
    updateUI(ui, state);
    setupListeners();
    loadQuestion();
  } catch (error) {
    console.error("Failed to init solids module:", error);
    ui.promptTitle.textContent = "Error loading content.";
  }
};

const updateToggleUI = () => {
  ui.adaptiveToggle.textContent = state.adaptive ? "On" : "Off";
  ui.adaptiveToggle.classList.toggle("off", !state.adaptive);
  ui.rigorToggle.textContent = state.rigorMode ? "On" : "Off";
  ui.rigorToggle.classList.toggle("off", !state.rigorMode);
};

const getPool = () => questionData[state.mode] || [];

const getNextQuestion = () => {
  const pool = getPool();
  if (state.adaptive && state.adaptiveQueue.length > 0) {
    return state.adaptiveQueue.shift();
  }
  return pool[Math.floor(Math.random() * pool.length)];
};

const loadQuestion = () => {
  const question = getNextQuestion();
  state.currentQuestion = question;
  state.selection = null;
  
  ui.modeBadge.textContent = ui.modeButtons.find((btn) => btn.dataset.mode === state.mode)?.textContent || "Module";
  ui.promptBadge.textContent = question.badge || "Solid state";
  ui.promptTitle.textContent = question.prompt;
  ui.promptNote.textContent = question.note;
  
  ui.feedback.className = "feedback";
  ui.feedback.textContent = "";
  
  renderDiagramPanel(question);
  renderOptions();
};

const renderDiagramPanel = (question) => {
  ui.diagramPanel.innerHTML = "";
  if (question.image) {
    const img = createElement("img", "chart-image");
    img.src = question.image;
    img.alt = "Unit cell";
    ui.diagramPanel.appendChild(img);
  } else {
    ui.diagramPanel.appendChild(createElement("p", "question-note", question.note));
  }
};

const renderOptions = () => {
  ui.answerZone.innerHTML = "";
  const block = createElement("div", "answer-block");
  block.appendChild(createElement("h4", "", "Select the best answer"));
  
  const grid = createElement("div", "option-grid");
  let options = [];
  if (state.mode === "identify") options = ["simple cubic", "body-centered cubic", "face-centered cubic"];
  else if (state.mode === "count") options = ["1", "2", "4"];
  else if (state.mode === "packing") options = ["52%", "68%", "74%"];
  else options = ["cubic", "tetragonal", "hexagonal", "orthorhombic"];
  
  options.forEach((opt) => {
    const btn = createElement("button", "option-button", opt);
    btn.addEventListener("click", () => {
      state.selection = opt;
      grid.querySelectorAll(".option-button").forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
    });
    grid.appendChild(btn);
  });
  
  block.appendChild(grid);
  ui.answerZone.appendChild(block);
};

const checkAnswer = () => {
  if (!state.currentQuestion || !state.selection) return;
  
  const isCorrect = state.selection.toLowerCase() === state.currentQuestion.answer.toLowerCase();
  
  state.total++;
  if (isCorrect) {
    state.correct++;
    state.streak++;
  } else {
    state.streak = 0;
    enqueueAdaptive(state.currentQuestion);
  }
  
  ui.feedback.className = `feedback ${isCorrect ? "success" : "error"}`;
  ui.feedback.textContent = isCorrect ? "Correct." : `Expected: ${state.currentQuestion.answer}.`;
  
  updateUI(ui, state);
};

const enqueueAdaptive = (q) => {
  if (!state.adaptive) return;
  const pool = getPool().filter(i => i.id !== q.id);
  if (pool.length) {
    state.adaptiveQueue.push(pool[Math.floor(Math.random() * pool.length)]);
  }
};

const setupListeners = () => {
  ui.modeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      ui.modeButtons.forEach((b) => b.classList.remove("active"));
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
    updateToggleUI(); saveSettings(settingsKey, state);
  });
};

init();