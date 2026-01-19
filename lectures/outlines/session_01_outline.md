# Session 1: Periodic Trends - LECTURE OUTLINE

## Source Strategy (from 9-Dimension Matrix)

| Role | Source | Why |
|------|--------|-----|
| **Narrative backbone** | JD Lee | Flesch 51.2 (most readable), 50% why:what ratio, short sentences (14 words avg) |
| **Visuals & diagrams** | Housecroft | 74 figures, high visual density, famous arrow diagrams for trends |
| **Worked examples** | Douglas | Many worked examples, occasional analogies |
| **Readable explanations** | House | Low jargon (13.7/1000), occasional analogies |
| **Quantitative depth** | Atkins | When we need rigor for Slater's rules calculations |

---

## The Story Arc (NOT bullet points)

### Act I: The Mystery (5 min)
**Opening hook:** Why can a chemist look at the periodic table and PREDICT that francium will explode more violently than sodium in water, without ever having seen francium react?

The periodic table isn't a filing cabinet—it's a prediction machine. Mendeleev predicted gallium's properties before it was discovered. How?

**Source:** JD Lee's historical narrative on Mendeleev's predictions

---

### Act II: The Hidden Variable (15 min)

#### Scene 1: Nuclear Charge Isn't the Whole Story

Start with the naive expectation: "More protons = stronger pull on electrons = smaller atom."

But wait—why is sodium (11 protons) LARGER than lithium (3 protons)? If more protons meant tighter grip, every element should be smaller than the one before.

**The reveal:** Electrons shield each other. The outer electron doesn't feel all 11 protons—it feels an *effective* nuclear charge.

**Visual (Housecroft):**
- Diagram showing inner electrons as a "shield" between nucleus and outer electron
- The famous "onion layer" model of electron shells

#### Scene 2: Slater's Rules - Quantifying the Shield

**Narrative (JD Lee):** Slater didn't guess—he analyzed thousands of experimental measurements and found patterns in how much each electron shields.

**The rules as a story, not a list:**
- Electrons in your own shell? Partial traitors—they shield a little (0.35)
- Electrons one shell deeper? Serious blockers (0.85)
- Electrons two or more shells in? Complete walls (1.00)

**Worked Example (Douglas style):**

*Calculate Z_eff for the outermost electron in oxygen.*

Not: "Apply formula."

Instead: "Let's trace what that 2p electron actually experiences..."

1. The nucleus screams "+8!"
2. But two 1s electrons stand in the way, each blocking 0.85 → that's 1.70 of charge absorbed
3. Five other electrons share the 2nd shell, each partially blocking (0.35 × 5 = 1.75)
4. What gets through? 8 - 1.70 - 1.75 = **4.55**

That electron feels less than half the nuclear charge. The shield is real.

**Visual (create):** Side-by-side comparison
- Left: "Naive view" - electron sees Z=8
- Right: "Reality" - electron sees Z_eff=4.55

---

### Act III: The Four Trends (25 min)

**Transition:** Now that we have Z_eff, we can explain EVERYTHING.

#### Trend 1: Atomic Radius

**Visual (Housecroft):** The famous arrow diagram
```
        ← DECREASING radius across period →
    ↓
    I
    N   Li  Be  B   C   N   O   F   Ne
    C   152 112 85  77  75  73  72  --  (pm)
    R
    E   Na  Mg  Al  Si  P   S   Cl  Ar
    A   186 160 143 118 110 103 99  --
    S
    I   K   Ca  ...
    N   227 197
    G
    ↓
```

**The story:**
- Across: More protons, same shell → Z_eff increases → electrons pulled in → SMALLER
- Down: New shell each row → electrons farther out → LARGER (even though Z_eff also increases!)

**The competition:** Z_eff vs. principal quantum number. Down a group, n wins.

**Analogy (House):** "Adding a floor to a building makes it taller, even if you also strengthen the foundation."

#### Trend 2: Ionization Energy

**Hook:** Which is easier—stealing a wallet from someone's back pocket, or from a safe?

**Visual (Housecroft):** IE vs atomic number graph showing the sawtooth pattern

**The main story:**
- High Z_eff = tight grip = high IE
- Across period: Z_eff increases → IE increases
- Down group: electron farther away → IE decreases

**The anomalies (this is where it gets interesting):**

*Why is IE(O) < IE(N)?*

**Visual (create):** Orbital box diagrams
```
N: [↑↓] [↑][↑][↑]     ← Half-filled 2p, stable
    2s    2p

O: [↑↓] [↑↓][↑][↑]   ← One orbital has paired electrons, repulsion!
    2s    2p
```

**Narrative:** Nitrogen's half-filled 2p is unusually stable (exchange energy). Oxygen has to cram two electrons into one orbital—they repel each other. Easier to remove.

*Why is IE(B) < IE(Be)?*

Beryllium's electron is in a 2s orbital (penetrates closer to nucleus). Boron's is in 2p (farther out, less penetrating). Even though B has more protons, that 2p electron is easier to grab.

**Real-world connection (Housecroft):** This is why alkaline earth metals can form +2 ions easily—losing two electrons empties their s orbital completely.

#### Trend 3: Electron Affinity

**Setup:** Ionization energy is about losing electrons. Electron affinity is about gaining them.

**The surprise:** Chlorine has higher EA than fluorine.

Wait—fluorine is MORE electronegative. Shouldn't it want electrons more?

**Visual (create):** Electron density maps
- F: tiny atom, electrons already crowded
- Cl: larger atom, more room for incoming electron

**Narrative (JD Lee):** Fluorine is SO small that adding another electron creates intense repulsion with the existing electrons. Chlorine has more space. Sometimes being too eager backfires.

**Data table (Basset):**
| Element | EA (kJ/mol) | Explanation |
|---------|-------------|-------------|
| F | 328 | Small size, electron crowding |
| Cl | 349 | Optimal size, highest EA |
| Br | 325 | Larger, lower Z_eff |
| I | 295 | Even larger |

#### Trend 4: Electronegativity

**Narrative:** Pauling invented electronegativity because he noticed something strange about bond energies.

H-H bond: 436 kJ/mol
F-F bond: 158 kJ/mol
H-F bond: 568 kJ/mol (way more than average!)

**The insight:** When atoms share electrons unequally, the bond is strengthened by ionic character. Pauling quantified how much each atom "pulls."

**Visual (Housecroft):** Electronegativity periodic table with color gradient

**The formula:**
χA - χB = 0.102√Δ

where Δ = D(A-B) - ½[D(A-A) + D(B-B)]

**Worked example (Douglas):** Calculate electronegativity difference for HCl...

**Connection:** Electronegativity combines IE and EA—it's the atom's total "electron hunger."

---

### Act IV: The Diagonal Relationships (10 min)

**Hook:** Lithium doesn't act like sodium. It acts like MAGNESIUM. Why?

**Visual (Housecroft):** Diagonal relationship arrows on periodic table
```
Li ----→ Mg
   ↘
Be ----→ Al
   ↘
B  ----→ Si
```

**The explanation:** Moving right increases Z_eff (smaller, more polarizing). Moving down decreases it (larger, less polarizing). Moving diagonally RIGHT-DOWN, these effects CANCEL.

Li and Mg have similar:
- Charge density (charge/radius ratio)
- Polarizing power
- Therefore similar chemistry

**Examples:**
- Li and Mg both form nitrides directly (Na doesn't)
- Li and Mg carbonates decompose on heating (Na's doesn't)
- Li and Mg hydroxides are weakly basic (Na's is strong)

---

### Act V: Why This Matters (5 min)

**Return to the opening:** Now you can do what Mendeleev did.

**Challenge:** Predict properties of element 119 (not yet synthesized):
- Atomic radius? (larger than Fr)
- Ionization energy? (lower than Fr)
- Reactivity with water? (more violent than Fr, if it's stable enough to observe)

**The periodic table as a roadmap:** Every prediction in chemistry starts here. Crystal field theory? Need to know ligand electronegativities. Acid-base chemistry? Need to know oxide basicity trends. Redox? Need to know ionization energies.

---

## Visual Assets Needed

| Visual | Source | Description |
|--------|--------|-------------|
| Fig 1 | Housecroft | Arrow diagram showing radius/IE/EN trends |
| Fig 2 | Create | Z_eff shielding diagram |
| Fig 3 | Housecroft | IE vs atomic number sawtooth graph |
| Fig 4 | Create | Orbital diagrams for N vs O anomaly |
| Fig 5 | Housecroft | Electronegativity color map |
| Fig 6 | Housecroft | Diagonal relationship arrows |

---

## Interactive Elements

| Element | Purpose |
|---------|---------|
| Slater's rules calculator | Input element → see Z_eff calculation step by step |
| Periodic table hover | Show all properties for any element |
| Trend prediction quiz | "Which is larger: S or Cl?" with explanation |
| Anomaly explorer | Click on any "exception" to see why |

---

## Estimated Length

| Section | Time | Words (prose) |
|---------|------|---------------|
| Act I: Mystery | 5 min | 400 |
| Act II: Z_eff | 15 min | 1200 |
| Act III: Four Trends | 25 min | 2000 |
| Act IV: Diagonal | 10 min | 800 |
| Act V: Why It Matters | 5 min | 400 |
| **Total** | **60 min** | **~4800 words** |

---

## Tone Guide

**DO:**
- Tell a story with tension and resolution
- Use analogies (House, Douglas style)
- Show calculations as detective work, not formulas
- Explain anomalies as the interesting part, not exceptions to memorize
- Connect to real chemistry (why this matters for coordination, acids, etc.)

**DON'T:**
- Bullet point lists of facts
- "The trend is X because Y" without building to it
- Skip the anomalies
- Assume students know why they should care
- Use jargon without earning it

---

*This outline produces a lecture that reads like a chapter, not a summary.*
