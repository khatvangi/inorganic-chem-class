# Session 1: The Periodic Table - A Complete Inorganic Perspective

**Level:** CHEM 361 Inorganic Chemistry (NOT Gen Chem!)
**Duration:** 90 minutes (expanded)
**Philosophy:** The periodic table isn't 4 trends to memorize—it's a map of electron behavior that explains ALL of inorganic chemistry.

---

## What Gen Chem Teaches vs. What IC Requires

| Gen Chem (insufficient) | Inorganic Chemistry (this lecture) |
|------------------------|-----------------------------------|
| 4 trends: radius, IE, EA, EN | Why trends BREAK and what that reveals |
| s and p block only | d-block anomalies, f-block behavior |
| Slater's rules (approximate) | Why Slater fails for d/f electrons |
| -- | Lanthanide contraction |
| -- | Relativistic effects |
| -- | Inert pair effect |
| -- | Why Hg is liquid, Au is golden |
| -- | Why lanthanides are nearly identical |
| -- | Periodicity of oxidation states |

---

## The Story Arc

### Part I: The Electronic Architecture (20 min)

**Opening:** Every element's chemistry is written in its electron configuration. But the aufbau principle lies to you.

#### 1.1 The Aufbau "Exceptions" Aren't Exceptions

The standard teaching: electrons fill orbitals in order of increasing energy (1s → 2s → 2p → 3s → 3p → 4s → 3d...).

Reality: **21 elements** don't follow this "rule." They're not exceptions—the rule is wrong.

**d-block anomalies:**
| Element | Expected | Actual | Why |
|---------|----------|--------|-----|
| Cr | [Ar] 3d⁴ 4s² | [Ar] 3d⁵ 4s¹ | Half-filled d subshell |
| Cu | [Ar] 3d⁹ 4s² | [Ar] 3d¹⁰ 4s¹ | Filled d subshell |
| Mo | [Kr] 4d⁴ 5s² | [Kr] 4d⁵ 5s¹ | Same pattern |
| Ag | [Kr] 4d⁹ 5s² | [Kr] 4d¹⁰ 5s¹ | Same pattern |
| Au | [Xe] 4f¹⁴ 5d⁹ 6s² | [Xe] 4f¹⁴ 5d¹⁰ 6s¹ | + relativistic contraction |

**The deeper truth:** d-d exchange energy and pairing energy compete. When the exchange energy gain from having parallel spins exceeds the orbital energy cost, electrons rearrange.

#### 1.2 The f-block Configuration Chaos

Lanthanides and actinides are even messier:
- La: [Xe] 5d¹ 6s² (no 4f!)
- Ce: [Xe] 4f¹ 5d¹ 6s²
- Gd: [Xe] 4f⁷ 5d¹ 6s² (half-filled f + one d)
- Lu: [Xe] 4f¹⁴ 5d¹ 6s²

**Visual:** Full periodic table with actual electron configurations, color-coded by anomaly type.

---

### Part II: The Three Contractions (25 min)

**The Big Idea:** Three "contractions" shape the periodic table, and understanding them explains most of inorganic chemistry.

#### 2.1 The Scandide Contraction (3d)

Moving across the first transition series (Sc → Zn), atoms get smaller even though electrons are being added. Why?

**3d electrons are poor shielders.** They spend most of their time far from the nucleus and can't effectively block nuclear charge from the 4s electrons.

Result: Ga (Z=31) is almost the same size as Al (Z=13), even with 18 more protons.

**Data (covalent radii, pm):**
```
Al: 121    Ga: 122    (only 1 pm difference!)
Si: 111    Ge: 120
P:  107    As: 119
```

#### 2.2 The Lanthanide Contraction (4f)

**The most important contraction for understanding heavy element chemistry.**

4f orbitals shield even worse than 3d. As we fill the 4f subshell (Ce → Lu), the nuclear charge felt by outer electrons increases dramatically.

Result: The 5d elements (Hf → Hg) are almost the same size as the 4d elements (Zr → Cd).

**Data (covalent radii, pm):**
| 4d | r | 5d | r | Difference |
|----|---|----|----|------------|
| Zr | 175 | Hf | 175 | 0 pm! |
| Nb | 164 | Ta | 170 | 6 pm |
| Mo | 154 | W | 162 | 8 pm |

**Consequences:**
- Zr/Hf and Nb/Ta are nearly impossible to separate chemically
- 5d metals are denser than expected (W, Os, Ir, Pt)
- Explains the "uniqueness" of the first row transition metals

#### 2.3 The Relativistic Contraction (6s)

**Here's where it gets wild.**

For heavy elements (Z > 70), electrons move so fast that relativistic effects become significant. The 1s electron in gold moves at ~58% the speed of light.

**Einstein's special relativity:** As velocity approaches c, mass increases:
```
m_rel = m₀ / √(1 - v²/c²)
```

Heavier electrons orbit closer to the nucleus → **6s orbital contracts**.

But it gets weirder: the contracted 6s orbital shields the nucleus better, so **5d and 4f orbitals expand**.

**The consequences are spectacular:**

| Element | Effect | Observable Result |
|---------|--------|-------------------|
| Au | 6s contracts, 5d expands | Gold is GOLD (5d→6s transition in visible) |
| Hg | 6s² very stable | Mercury is LIQUID (weak Hg-Hg bonds) |
| Pb | 6s² inert | Lead is +2, not +4 like C, Si, Ge, Sn |
| W | 5d expanded | Highest melting point of any element |

**Visual:** Orbital contraction/expansion diagram showing relativistic vs non-relativistic radii.

---

### Part III: The Inert Pair Effect (15 min)

**The puzzle:** Why does Tl prefer +1 over +3? Why is Pb²⁺ more stable than Pb⁴⁺?

Down a group, the ns² electrons become increasingly reluctant to participate in bonding.

| Group 13 | Common oxidation state |
|----------|----------------------|
| Al | +3 only |
| Ga | +3 (some +1) |
| In | +3 (more +1) |
| Tl | +1 preferred, +3 oxidizing |

**Two explanations (both contribute):**

1. **Relativistic stabilization** of the 6s orbital makes it energetically costly to use those electrons.

2. **Poor orbital overlap:** 6s orbitals are contracted; 6p orbitals are expanded. The size mismatch with ligand orbitals makes bonds weaker.

**Real chemistry:**
- TlCl is stable; TlCl₃ decomposes above 40°C
- PbO₂ is a powerful oxidizer (wants to become PbO)
- Bi₂O₅ doesn't exist; Bi₂O₃ is stable

---

### Part IV: The f-Block - Why Lanthanides Are "Boring" (15 min)

**The paradox:** 15 elements (La-Lu) with remarkably similar chemistry. Why?

**4f orbitals are buried.** They're shielded by filled 5s, 5p, and partially filled 5d/6s orbitals. The 4f electrons rarely participate directly in bonding.

**Consequences:**
- All lanthanides favor +3 oxidation state
- Ionic radii decrease smoothly (lanthanide contraction)
- Similar coordination chemistry
- Hard to separate (requires ion exchange chromatography)

**The few exceptions reveal what matters:**
- Ce⁴⁺ exists (one 4f electron easily removed → noble gas core)
- Eu²⁺ exists (half-filled 4f⁷ is stable)
- Yb²⁺ exists (filled 4f¹⁴ is stable)

**Actinides are different:**
- 5f orbitals extend further, participate more in bonding
- Multiple oxidation states common (U: +3 to +6)
- More covalent character

---

### Part V: Periodicity of Oxidation States (10 min)

**Maximum oxidation state:**
- Equals group number up to Mn/Re (Group 7)
- Then decreases (Fe: max +6, Co: max +5, Ni: max +4)
- Noble metals resist oxidation (Pt, Au)

**Pattern across periods:**

Period 4 (3d):
```
Sc  Ti  V   Cr  Mn  Fe  Co  Ni  Cu  Zn
+3  +4  +5  +6  +7  +6  +4  +4  +2  +2
        (maximum oxidation states)
```

**Why the decrease after Mn?**

Exchange energy stabilization. More d electrons = more stability from parallel spins = harder to remove electrons.

---

### Part VI: Why Mercury Is Liquid (5 min)

**The question every student asks.**

Mercury melts at -39°C. The next lowest melting metal is cesium at 28°C. What's special about Hg?

**The answer combines everything:**

1. **Relativistic 6s contraction:** Hg's 6s² electrons are pulled very close to the nucleus.

2. **Filled d-shell:** 5d¹⁰ provides no bonding orbitals.

3. **Weak metallic bonding:** The contracted 6s orbital overlaps poorly with neighbors.

4. **No d-band contribution:** Unlike other metals where d orbitals strengthen the metallic bond, Hg's filled 5d contributes nothing.

Result: Hg atoms barely stick together → liquid at room temperature.

**Comparison:**
- Cd (same group, no relativistic effect): melts at 321°C
- Au (one less electron, 5d¹⁰ 6s¹): excellent metallic bonding, melts at 1064°C

---

## Interactive Elements Needed

| Element | Purpose |
|---------|---------|
| Full periodic table | Hover for electron config, click for anomalies |
| Radii comparison | Side-by-side 4d vs 5d elements |
| Relativistic calculator | Show how v/c affects orbital size |
| Oxidation state explorer | Click element → show all known oxidation states |
| Lanthanide separation | Animate ion exchange chromatography |

---

## Visual Assets

1. **Periodic table with electron configurations** - color-coded by anomaly type
2. **Orbital radial distribution** - showing 4f vs 5d penetration
3. **Relativistic vs non-relativistic orbital sizes** - for Au, Hg, Pb
4. **Lanthanide contraction graph** - ionic radii La³⁺ → Lu³⁺
5. **Gold absorption spectrum** - why it's golden
6. **Oxidation state heatmap** - periodic table colored by max ox state

---

## Data Sources

- Atomic radii: Cordero et al. 2008
- Electron configurations: NIST
- Relativistic calculations: Pyykkö 1988, Chem. Rev.
- Ionization energies: NIST ASD
- Oxidation states: Greenwood & Earnshaw

---

*This is what a CHEM 361 lecture on periodicity should cover.*
