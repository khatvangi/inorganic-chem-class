import { createElement } from "../js/utils.js";

const state = {
  lectureData: null,
  galleryData: {},
};

const ui = {
  container: document.getElementById("slideContainer"),
  stageNote: document.getElementById("stageNote"),
};

let viewer = null;

const init = async () => {
  try {
    const lRes = await fetch("../data/lectures/mo_theory.json");
    state.lectureData = await lRes.json();

    const gRes = await fetch("../data/symmetry_gallery.json");
    const galleryList = await gRes.json();
    galleryList.forEach(m => state.galleryData[m.name] = m);

    // Setup Lecture specifics
    state.galleryData["H2"] = { atoms: [{element:"H", x:0.7, y:0, z:0}, {element:"H", x:-0.7, y:0, z:0}] };
    state.galleryData["O2"] = { atoms: [{element:"O", x:0.6, y:0, z:0}, {element:"O", x:-0.6, y:0, z:0}] };
    state.galleryData["CO"] = { atoms: [{element:"C", x:0.55, y:0, z:0}, {element:"O", x:-0.55, y:0, z:0}] };

    initViewer();
    renderSlides();
    setupObserver();

  } catch (e) {
    console.error("Init error:", e);
  }
};

const initViewer = () => {
  if (typeof ChemDoodle === "undefined") return;
  const canvas = document.getElementById("chemDoodle3D");
  canvas.width = canvas.parentElement.clientWidth;
  canvas.height = canvas.parentElement.clientHeight;
  
  viewer = new ChemDoodle.ViewerCanvas3D("chemDoodle3D", canvas.width, canvas.height);
  viewer.styles.backgroundColor = "#1a1a1a";
  viewer.styles.atoms_useJMOLColors = true;
  viewer.styles.bonds_color = "white";
  viewer.styles.atoms_sphereDiameter_3D = 0.8;
};

const renderSlides = () => {
  state.lectureData.sections.forEach(section => {
    const card = createElement("div", "slide-card");
    card.dataset.id = section.id;
    
    const h2 = createElement("h2", "", section.title);
    const p = createElement("div", "");
    p.innerHTML = section.content;
    
    card.appendChild(h2);
    card.appendChild(p);
    ui.container.appendChild(card);
  });
};

const updateStage = (sectionId) => {
  const section = state.lectureData.sections.find(s => s.id === sectionId);
  if (!section || !section.visuals || section.visuals.length === 0) return;

  const visual = section.visuals[0];
  ui.stageNote.textContent = visual.note || "";

  if (visual.type === "chemDoodle" && viewer) {
    const molData = state.galleryData[visual.molecule];
    if (molData) loadMolecule(molData);
  }
};

const loadMolecule = (data) => {
  const mol = new ChemDoodle.structures.Molecule();
  data.atoms.forEach(a => {
    const atom = new ChemDoodle.structures.Atom(a.element);
    atom.x = a.x * 2;
    atom.y = a.y * 2;
    atom.z = a.z * 2;
    mol.atoms.push(atom);
  });
  // Connect all for simple diatomics
  if (mol.atoms.length === 2) {
      mol.bonds.push(new ChemDoodle.structures.Bond(mol.atoms[0], mol.atoms[1]));
  } else {
      // Logic for H2O etc
      for(let i=0; i<mol.atoms.length; i++) {
          for(let j=i+1; j<mol.atoms.length; j++) {
              mol.bonds.push(new ChemDoodle.structures.Bond(mol.atoms[i], mol.atoms[j]));
          }
      }
  }
  viewer.loadMolecule(mol);
};

const setupObserver = () => {
  const options = { root: ui.container, threshold: 0.6 };
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        document.querySelectorAll(".slide-card").forEach(c => c.classList.remove("active"));
        entry.target.classList.add("active");
        updateStage(entry.target.dataset.id);
      }
    });
  }, options);
  document.querySelectorAll(".slide-card").forEach(card => observer.observe(card));
};

init();
