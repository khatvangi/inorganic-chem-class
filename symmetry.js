import { createElement } from "./js/utils.js";

let galleryData = [];
let viewer = null;

const ui = {
  moleculeList: document.getElementById("moleculeList"),
  molName: document.getElementById("molName"),
  pointGroupBadge: document.getElementById("pointGroupBadge"),
  symmetryList: document.getElementById("symmetryList"),
};

const init = async () => {
  try {
    const response = await fetch("./data/symmetry_gallery.json");
    galleryData = await response.json();
    
    initViewer();
    renderSidebar();
    
    if (galleryData.length > 0) {
      loadMolecule(galleryData[0]);
    }
  } catch (error) {
    console.error("Failed to init symmetry gallery:", error);
  }
};

const initViewer = () => {
  if (typeof ChemDoodle === "undefined") return;
  
  viewer = new ChemDoodle.ViewerCanvas3D("chemDoodle3D", 500, 400);
  viewer.styles.backgroundColor = "white";
  viewer.styles.atoms_useJMOLColors = true;
  viewer.styles.bonds_color = "black";
  viewer.styles.atoms_sphereDiameter_3D = 0.6;
};

const renderSidebar = () => {
  ui.moleculeList.innerHTML = "";
  galleryData.forEach((mol) => {
    const btn = createElement("button", "option-button", mol.name);
    btn.addEventListener("click", () => {
      // Toggle active class
      Array.from(ui.moleculeList.children).forEach(c => c.classList.remove("active"));
      btn.classList.add("active");
      loadMolecule(mol);
    });
    ui.moleculeList.appendChild(btn);
  });
};

const loadMolecule = (data) => {
  ui.molName.textContent = data.name;
  ui.pointGroupBadge.textContent = data.pointGroup || "Unknown";
  
  // Update List
  ui.symmetryList.innerHTML = "";
  if (data.elements) {
    data.elements.forEach(el => {
      const li = createElement("li", "", el);
      ui.symmetryList.appendChild(li);
    });
  }

  // Render 3D
  if (!viewer) return;
  
  const mol = new ChemDoodle.structures.Molecule();
  
  // Create atoms
  const atomObjects = data.atoms.map(a => {
    const atom = new ChemDoodle.structures.Atom(a.element);
    atom.x = a.x * 1.5; // Scale for visibility
    atom.y = a.y * 1.5;
    atom.z = a.z * 1.5;
    mol.atoms.push(atom);
    return atom;
  });

  // Infer bonds (simple distance check for visualization)
  for (let i = 0; i < atomObjects.length; i++) {
    for (let j = i + 1; j < atomObjects.length; j++) {
      const a1 = atomObjects[i];
      const a2 = atomObjects[j];
      const dist = Math.sqrt(
        Math.pow(a1.x - a2.x, 2) + 
        Math.pow(a1.y - a2.y, 2) + 
        Math.pow(a1.z - a2.z, 2)
      );
      
      // Rough bond threshold (scaled)
      if (dist < 2.8 && dist > 0.1) {
        mol.bonds.push(new ChemDoodle.structures.Bond(a1, a2));
      }
    }
  }

  viewer.loadMolecule(mol);
};

init();
