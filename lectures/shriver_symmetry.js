import { createElement } from "../js/utils.js";

const state = {
  lectureData: null,
  galleryData: {},
  currentVisual: null
};

const ui = {
  container: document.getElementById("slideContainer"),
  stageNote: document.getElementById("stageNote"),
};

let viewer = null;

const init = async () => {
  try {
    // Load Lecture Content
    const lRes = await fetch("../data/lectures/symmetry_shriver.json");
    state.lectureData = await lRes.json();

    // Load Molecule Data (Reuse our gallery)
    const gRes = await fetch("../data/symmetry_gallery.json");
    const galleryList = await gRes.json();
    galleryList.forEach(m => state.galleryData[m.name] = m);

    // Hardcode simple molecules if missing (backup)
    state.galleryData["H2O"] = state.galleryData["H2O"] || { atoms: [{element:"O", x:0, y:0, z:0}, {element:"H", x:0.8, y:0.6, z:0}, {element:"H", x:-0.8, y:0.6, z:0}] };
    state.galleryData["NH3"] = state.galleryData["NH3"] || { atoms: [{element:"N", x:0, y:0, z:0.1}, {element:"H", x:0.9, y:0, z:-0.3}, {element:"H", x:-0.45, y:0.8, z:-0.3}, {element:"H", x:-0.45, y:-0.8, z:-0.3}] };

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
  viewer.styles.backgroundColor = "#eef2f5";
  viewer.styles.atoms_useJMOLColors = true;
  viewer.styles.bonds_color = "black";
  viewer.styles.atoms_sphereDiameter_3D = 0.6;
};

const renderSlides = () => {
  state.lectureData.sections.forEach(section => {
    const card = createElement("div", "slide-card");
    card.dataset.id = section.id;
    
    const h2 = createElement("h2", "", section.title);
    const p = createElement("div", "");
    p.innerHTML = section.content; // Allow HTML for math/bold
    
    card.appendChild(h2);
    card.appendChild(p);
    ui.container.appendChild(card);
  });
};

const updateStage = (sectionId) => {
  const section = state.lectureData.sections.find(s => s.id === sectionId);
  if (!section || !section.visuals || section.visuals.length === 0) return;

  const visual = section.visuals[0]; // Take primary visual
  ui.stageNote.textContent = visual.note || "";

  if (visual.type === "chemDoodle" && viewer) {
    const molName = visual.molecule;
    const molData = state.galleryData[molName];
    
    if (molData) {
      loadMolecule(molData);
    } else {
      console.warn("Molecule not found:", molName);
    }
  }
};

const loadMolecule = (data) => {
  const mol = new ChemDoodle.structures.Molecule();
  const atomObjects = data.atoms.map(a => {
    const atom = new ChemDoodle.structures.Atom(a.element);
    atom.x = a.x * 1.5;
    atom.y = a.y * 1.5;
    atom.z = a.z * 1.5;
    mol.atoms.push(atom);
    return atom;
  });

  // Simple bond logic
  for (let i = 0; i < atomObjects.length; i++) {
    for (let j = i + 1; j < atomObjects.length; j++) {
      const d = Math.sqrt(
        Math.pow(atomObjects[i].x - atomObjects[j].x, 2) + 
        Math.pow(atomObjects[i].y - atomObjects[j].y, 2) + 
        Math.pow(atomObjects[i].z - atomObjects[j].z, 2)
      );
      if (d < 3.0 && d > 0.1) {
        mol.bonds.push(new ChemDoodle.structures.Bond(atomObjects[i], atomObjects[j]));
      }
    }
  }
  viewer.loadMolecule(mol);
};

const setupObserver = () => {
  const options = {
    root: ui.container,
    threshold: 0.6 
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        // Highlight active card
        document.querySelectorAll(".slide-card").forEach(c => c.classList.remove("active"));
        entry.target.classList.add("active");
        
        // Update stage
        updateStage(entry.target.dataset.id);
      }
    });
  }, options);

  document.querySelectorAll(".slide-card").forEach(card => observer.observe(card));
};

init();
