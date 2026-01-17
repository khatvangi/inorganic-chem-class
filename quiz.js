import { createElement, normalizeAnswer } from "./js/utils.js";

const state = {
  questions: [],
  currentIndex: 0,
  score: 0,
  streak: 0,
  answered: false
};

const ui = {
  title: document.getElementById("quizTitle"),
  topic: document.getElementById("quizTopic"),
  score: document.getElementById("scoreDisplay"),
  streak: document.getElementById("streakDisplay"),
  qNum: document.getElementById("qNumBadge"),
  qTopic: document.getElementById("topicBadge"),
  text: document.getElementById("questionText"),
  viewerContainer: document.getElementById("viewerContainer"),
  options: document.getElementById("optionsGrid"),
  feedback: document.getElementById("feedback"),
  nextBtn: document.getElementById("nextBtn"),
};

let viewer = null;

const init = async () => {
  const params = new URLSearchParams(window.location.search);
  const quizId = params.get("id") || "symmetry_mo";
  
  try {
    // Load Quiz Data
    const response = await fetch(`./data/quizzes/${quizId}.json`);
    if (!response.ok) throw new Error("Quiz not found");
    
    state.questions = await response.json();
    
    // Set Titles
    ui.title.textContent = formatTitle(quizId);
    ui.topic.textContent = `${state.questions.length} Questions`;
    
    initViewer();
    loadQuestion();
    
    ui.nextBtn.addEventListener("click", nextQuestion);
    
  } catch (error) {
    console.error(error);
    ui.text.textContent = "Error loading quiz data.";
  }
};

const formatTitle = (id) => {
  return id.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
};

const initViewer = () => {
  if (typeof ChemDoodle === "undefined") return;
  viewer = new ChemDoodle.ViewerCanvas3D("chemDoodle3D", 400, 350);
  viewer.styles.backgroundColor = "white";
  viewer.styles.atoms_useJMOLColors = true;
  viewer.styles.bonds_color = "black";
  viewer.styles.atoms_sphereDiameter_3D = 0.6;
};

const loadQuestion = () => {
  const q = state.questions[state.currentIndex];
  state.answered = false;
  
  // Update Text
  ui.qNum.textContent = `Question ${state.currentIndex + 1} / ${state.questions.length}`;
  ui.qTopic.textContent = q.topic || "General";
  ui.text.textContent = q.question;
  
  // Render Viewer if diagram exists
  if (q.diagram && q.diagram.central && viewer) {
    ui.viewerContainer.style.display = "block";
    renderMolecule(q.diagram);
  } else {
    ui.viewerContainer.style.display = "none";
  }
  
  // Render Options
  ui.options.innerHTML = "";
  q.options.forEach(opt => {
    // Handle cases where options might be just "A", "B"... or full text
    // If just A/B, map to meaningful text if possible, otherwise display as is
    const btn = createElement("button", "option-button", opt);
    btn.dataset.value = opt; // or the letter if structured that way
    
    // Check if the option string starts with "A)", "B)", etc.
    const letterMatch = opt.match(/^([A-D])[\).]/);
    const letter = letterMatch ? letterMatch[1] : opt.charAt(0); // fallback
    
    btn.onclick = () => checkAnswer(letter, btn, q);
    ui.options.appendChild(btn);
  });
  
  ui.feedback.className = "feedback";
  ui.feedback.textContent = "";
  ui.nextBtn.disabled = true;
};

const renderMolecule = (diagram) => {
  const mol = new ChemDoodle.structures.Molecule();
  
  // Central Atom
  const center = new ChemDoodle.structures.Atom(diagram.central);
  center.x = 0; center.y = 0; center.z = 0;
  mol.atoms.push(center);
  
  // Ligands
  const coords = {
    top: {x:0, y:1.5, z:0},
    bottom: {x:0, y:-1.5, z:0},
    left: {x:-1.5, y:0, z:0},
    right: {x:1.5, y:0, z:0},
    front: {x:0, y:0, z:1.5},
    back: {x:0, y:0, z:-1.5}
  };
  
  if (diagram.ligands) {
    Object.entries(diagram.ligands).forEach(([pos, label]) => {
      if (!label || !coords[pos]) return;
      // Extract element symbol (e.g., "NH3" -> "N")
      let symbol = label.replace(/[0-9+\-]/g, "").charAt(0); 
      // Very basic element guesser
      if (["C","N","O","F","H","P","S","Cl","Br","I"].includes(label.charAt(0))) {
          symbol = label.charAt(0);
      }
      
      const atom = new ChemDoodle.structures.Atom(symbol);
      atom.x = coords[pos].x;
      atom.y = coords[pos].y;
      atom.z = coords[pos].z;
      mol.atoms.push(atom);
      mol.bonds.push(new ChemDoodle.structures.Bond(center, atom));
    });
  }
  
  viewer.loadMolecule(mol);
};

const checkAnswer = (userChoice, btn, question) => {
  if (state.answered) return;
  state.answered = true;
  
  // Normalize user choice (usually "A", "B", etc.)
  // The 'answer' field in JSON is usually just "A" or "B" or the full text.
  // We need to match robustly.
  
  const correctLetter = question.answer.charAt(0).toUpperCase(); // "A"
  const userLetter = userChoice.charAt(0).toUpperCase();
  
  const isCorrect = userLetter === correctLetter;
  
  if (isCorrect) {
    btn.classList.add("correct");
    state.score++;
    state.streak++;
  } else {
    btn.classList.add("incorrect");
    state.streak = 0;
    // Highlight correct
    Array.from(ui.options.children).forEach(b => {
      if (b.innerText.startsWith(correctLetter)) b.classList.add("correct");
    });
  }
  
  // Update UI
  ui.score.textContent = `${state.score} / ${state.questions.length}`;
  ui.streak.textContent = state.streak;
  
  ui.feedback.className = `feedback ${isCorrect ? "success" : "error"}`;
  ui.feedback.innerHTML = `<strong>${isCorrect ? "Correct!" : "Incorrect."}</strong> ${question.explanation}`;
  
  ui.nextBtn.disabled = false;
};

const nextQuestion = () => {
  state.currentIndex++;
  if (state.currentIndex < state.questions.length) {
    loadQuestion();
  } else {
    ui.text.textContent = "Quiz Complete!";
    ui.options.innerHTML = `<div class="panel-card">Final Score: ${state.score} / ${state.questions.length}</div>`;
    ui.viewerContainer.style.display = "none";
    ui.nextBtn.style.display = "none";
  }
};

init();
