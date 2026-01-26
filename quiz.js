import { createElement, normalizeAnswer } from "./js/utils.js";

const MAX_ATTEMPTS = 3;

const state = {
  questions: [],
  currentIndex: 0,
  score: 0,
  streak: 0,
  attempts: 0,        // attempts on current question
  answered: false,    // correctly answered
  hintsShown: [],     // which hints have been revealed
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
    const response = await fetch(`./data/quizzes/${quizId}.json`);
    if (!response.ok) throw new Error("Quiz not found");

    state.questions = await response.json();

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
  state.attempts = 0;
  state.hintsShown = [];

  // update header
  ui.qNum.textContent = `Question ${state.currentIndex + 1} / ${state.questions.length}`;
  ui.qTopic.textContent = q.topic || "General";
  ui.text.textContent = q.question;

  // render 3D viewer if diagram exists
  if (q.diagram && q.diagram.central && viewer) {
    ui.viewerContainer.style.display = "block";
    renderMolecule(q.diagram);
  } else {
    ui.viewerContainer.style.display = "none";
  }

  // render options
  ui.options.innerHTML = "";
  const letters = ["A", "B", "C", "D"];
  q.options.forEach((opt, index) => {
    // show option with letter prefix for clarity
    const letter = letters[index];
    const btn = createElement("button", "option-button", `${letter}. ${opt}`);
    btn.dataset.value = opt;
    btn.dataset.letter = letter;

    btn.onclick = () => checkAnswer(letter, btn, q);
    ui.options.appendChild(btn);
  });

  // clear feedback but keep structure
  ui.feedback.className = "feedback";
  ui.feedback.innerHTML = "";
  ui.nextBtn.disabled = true;
};

const renderMolecule = (diagram) => {
  const mol = new ChemDoodle.structures.Molecule();

  const center = new ChemDoodle.structures.Atom(diagram.central);
  center.x = 0; center.y = 0; center.z = 0;
  mol.atoms.push(center);

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
      let symbol = label.replace(/[0-9+\-]/g, "").charAt(0);
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

  const correctLetter = question.answer.charAt(0).toUpperCase();
  const userLetter = userChoice.charAt(0).toUpperCase();
  const isCorrect = userLetter === correctLetter;

  state.attempts++;

  if (isCorrect) {
    // correct answer
    state.answered = true;
    btn.classList.add("correct");
    state.score++;
    state.streak++;

    ui.score.textContent = `${state.score} / ${state.questions.length}`;
    ui.streak.textContent = state.streak;

    showFeedback("success", question, true);
    ui.nextBtn.disabled = false;

  } else {
    // wrong answer
    btn.classList.add("wrong");
    btn.disabled = true; // disable this wrong option
    state.streak = 0;
    ui.streak.textContent = state.streak;

    if (state.attempts >= MAX_ATTEMPTS) {
      // max attempts reached - reveal answer
      state.answered = true;

      // highlight correct answer
      Array.from(ui.options.children).forEach(b => {
        if (b.dataset.letter === correctLetter) {
          b.classList.add("correct");
        }
      });

      showFeedback("reveal", question, false);
      ui.nextBtn.disabled = false;

    } else {
      // show hint for this attempt
      showHint(question, state.attempts);
    }
  }
};

const showHint = (question, attemptNum) => {
  // build hint content based on attempt number
  let hintContent = "";

  // attempt 1: show first hint
  // attempt 2: show second hint or more detailed hint

  const hints = question.hints || [];
  const theory = question.theory || null;

  if (attemptNum === 1) {
    // first wrong attempt - show hint 1 or generic hint
    if (hints.length > 0) {
      hintContent = `<strong>Hint:</strong> ${hints[0]}`;
    } else if (question.explanation) {
      // extract a hint from the explanation (first sentence or part)
      const firstPart = question.explanation.split('.')[0];
      hintContent = `<strong>Hint:</strong> Think about ${firstPart.toLowerCase()}...`;
    } else {
      hintContent = `<strong>Hint:</strong> Try again! You have ${MAX_ATTEMPTS - attemptNum} attempts remaining.`;
    }
  } else if (attemptNum === 2) {
    // second wrong attempt - show hint 2 or theory pointer
    if (hints.length > 1) {
      hintContent = `<strong>Hint 2:</strong> ${hints[1]}`;
    } else if (theory) {
      hintContent = `<strong>Theory pointer:</strong> Review <a href="${theory.link}" target="_blank">${theory.topic}</a>`;
    } else {
      hintContent = `<strong>Last chance!</strong> One more attempt remaining.`;
    }

    // add theory link if available
    if (theory && hints.length <= 1) {
      hintContent += `<br><span class="theory-link">📖 Related concept: <a href="${theory.link}" target="_blank">${theory.topic}</a></span>`;
    }
  }

  // preserve previous hints and add new one
  const existingHints = ui.feedback.innerHTML;

  ui.feedback.className = "feedback hint";
  ui.feedback.innerHTML = existingHints
    ? existingHints + `<div class="hint-item">${hintContent}</div>`
    : `<div class="hint-item">${hintContent}</div>`;
};

const showFeedback = (type, question, wasCorrect) => {
  const theory = question.theory || null;

  let content = "";

  if (type === "success") {
    content = `<div class="feedback-header success">✓ Correct!</div>`;
    if (question.explanation) {
      content += `<div class="explanation">${question.explanation}</div>`;
    }
  } else if (type === "reveal") {
    content = `<div class="feedback-header reveal">Answer revealed after ${MAX_ATTEMPTS} attempts</div>`;
    if (question.explanation) {
      content += `<div class="explanation">${question.explanation}</div>`;
    }

    // offer similar question practice
    content += `<div class="practice-prompt">
      <strong>Want more practice?</strong>
      <button class="practice-btn" onclick="generateSimilarQuestion()">Try a similar question</button>
    </div>`;
  }

  // add theory link
  if (theory) {
    content += `<div class="theory-section">
      <span class="theory-icon">📖</span>
      <strong>Learn more:</strong>
      <a href="${theory.link}" target="_blank">${theory.topic}</a>
    </div>`;
  }

  ui.feedback.className = `feedback ${type}`;
  ui.feedback.innerHTML = content;
};

// generate a similar question (simplified version - could be enhanced with AI)
window.generateSimilarQuestion = () => {
  const currentQ = state.questions[state.currentIndex];

  // for now, find another question with the same topic
  const sameTopic = state.questions.filter((q, i) =>
    i !== state.currentIndex && q.topic === currentQ.topic
  );

  if (sameTopic.length > 0) {
    // insert similar question after current
    const similar = sameTopic[Math.floor(Math.random() * sameTopic.length)];
    const clone = JSON.parse(JSON.stringify(similar));
    clone.topic = `${clone.topic} (Practice)`;

    // insert after current question
    state.questions.splice(state.currentIndex + 1, 0, clone);
    ui.topic.textContent = `${state.questions.length} Questions`;

    ui.feedback.innerHTML += `<div class="practice-added">✓ Similar question added! Click "Next" to try it.</div>`;
  } else {
    ui.feedback.innerHTML += `<div class="practice-added">No similar questions available for this topic.</div>`;
  }
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
    ui.feedback.innerHTML = "";
  }
};

init();
