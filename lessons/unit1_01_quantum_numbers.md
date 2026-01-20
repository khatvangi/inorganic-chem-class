# Unit 1, Lesson 1: Quantum Numbers — Why Integers Rule the Atom

**Interactive:** [quantum_numbers_explorer.html](visuals/quantum_numbers_explorer.html)

---

## The Question

Why can't an electron have any energy it wants?

In the macroscopic world, energy is continuous. A ball rolling down a hill can have any speed. But inside an atom, energy comes in discrete packets. An electron in hydrogen can have -13.6 eV, or -3.4 eV, or -1.5 eV — but nothing in between.

Why?

---

## The Answer: Waves Must Fit

An electron isn't a tiny ball orbiting the nucleus. It's described by a **wave function** ψ — a mathematical wave that tells us where we might find the electron.

Like any wave, ψ must satisfy **boundary conditions**:
- It must go to zero far from the nucleus (the electron is bound)
- It must be continuous and smooth (no breaks or kinks)
- It must connect to itself when you go around the atom

**Only certain waves fit these conditions.**

Think of a guitar string. It's fixed at both ends. It can vibrate at its fundamental frequency, or twice that, or three times — but nothing in between. The integer that counts how many half-wavelengths fit on the string determines the pitch.

The quantum numbers are exactly like this. They count how many times the wave "fits" in different directions.

---

## The Four Quantum Numbers

Each quantum number emerges from a boundary condition:

### n — The Principal Quantum Number

**What it counts:** How many times the radial wave oscillates before decaying to zero.

**Physical meaning:** Determines the size and energy of the orbital. Higher n = electron further from nucleus = higher energy.

**Allowed values:** 1, 2, 3, 4, ... (positive integers)

**Where it comes from:** The radial boundary condition. At infinite distance, ψ must decay to zero. Only certain energies allow this smooth decay. These energies are:

```
E_n = -13.6 eV × Z²/n²
```

The spacing between levels gets smaller as n increases — they converge toward zero (ionization).

---

### l — The Angular Momentum Quantum Number

**What it counts:** The number of angular nodes (surfaces where ψ = 0 that pass through the nucleus).

**Physical meaning:** Determines the shape of the orbital.

| l | Letter | Shape | Angular nodes |
|---|--------|-------|---------------|
| 0 | s | spherical | 0 |
| 1 | p | dumbbell | 1 plane |
| 2 | d | cloverleaf | 2 planes |
| 3 | f | complex | 3 surfaces |

**Allowed values:** 0, 1, 2, ..., (n-1)

**Where it comes from:** The angular boundary condition. As you go around the atom, the wave must connect smoothly to itself. The number of times it crosses zero determines l.

**Why l < n:** The total number of nodes is always n - 1. Some are radial, some are angular. If l angular nodes exist, only n - l - 1 radial nodes remain. You can't have more angular nodes than the total allows.

---

### mₗ — The Magnetic Quantum Number

**What it counts:** The orientation of the angular momentum in space.

**Physical meaning:** Specifies which orbital of a given shape (px vs py vs pz, for example).

**Allowed values:** -l, -l+1, ..., 0, ..., l-1, l (that's 2l + 1 values)

**Where it comes from:** The angular momentum vector has a definite magnitude (determined by l) but can point in 2l + 1 directions relative to any chosen axis. In a magnetic field, these orientations have different energies — hence "magnetic" quantum number.

**Example:** For l = 1 (p orbitals), mₗ can be -1, 0, or +1. That's three p orbitals, pointing in three perpendicular directions.

---

### mₛ — The Spin Quantum Number

**What it counts:** The intrinsic angular momentum of the electron itself.

**Physical meaning:** Every electron spins (in a quantum mechanical sense) and can only spin "up" or "down."

**Allowed values:** +½ or -½

**Where it comes from:** This one is different. It's not from orbital motion — it's built into the electron itself. The electron has intrinsic angular momentum just as it has intrinsic charge and mass.

**The crucial rule:** Two electrons can share an orbital only if they have opposite spins. This is the Pauli exclusion principle — no two electrons can have all four quantum numbers identical.

---

## Counting Nodes

Nodes are surfaces where ψ = 0. Two types:

**Radial nodes:** Spherical shells where the radial wave function R(r) crosses zero.
- Count: **n - l - 1**
- A 3s orbital has 3 - 0 - 1 = 2 radial nodes

**Angular nodes:** Planar or conical surfaces through the nucleus.
- Count: **l**
- A 3d orbital has l = 2 angular nodes

**Total nodes = n - 1** (always)

This is why quantum numbers are linked: they're dividing up a fixed node budget.

---

## Why Energy Depends on Both n and l

In hydrogen (one electron), all orbitals with the same n have the same energy. 2s = 2p. 3s = 3p = 3d. They're **degenerate**.

In many-electron atoms, this degeneracy breaks. 2s < 2p in energy. Why?

**Shielding and penetration.**

Inner electrons shield outer electrons from the full nuclear charge. But s electrons penetrate closer to the nucleus than p electrons (look at the radial distribution — s has more probability near r = 0). So s electrons "feel" more of the nuclear charge and are more tightly bound.

The result: **s < p < d < f** in energy for the same n.

This is why the building-up order isn't simply 1s, 2s, 2p, 3s, 3p, 3d, 4s... Instead, 4s fills before 3d in potassium. The 4s orbital, despite higher n, penetrates better and ends up lower in energy than 3d.

---

## The Big Picture

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│   BOUNDARY CONDITIONS  →  WAVES THAT FIT  →  INTEGERS        │
│                                                              │
│   Radial decay         →  R(r) oscillates  →  n              │
│   Angular smoothness   →  Nodes through    →  l              │
│                           nucleus                            │
│   Spatial orientation  →  2l+1 directions  →  mₗ             │
│   Intrinsic property   →  Spin up/down     →  mₛ             │
│                                                              │
│   Together: (n, l, mₗ, mₛ) = one electron's complete state   │
│   Pauli: no two electrons can share all four                 │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

Quantum numbers aren't arbitrary labels invented for bookkeeping. They emerge inevitably from the mathematics of waves confined by boundary conditions. The integers count real things — oscillations, nodes, orientations.

The periodic table, chemical bonding, atomic spectra — all flow from these four numbers and the rules they follow.

---

## Check Your Understanding

1. A 4d orbital. How many radial nodes? How many angular nodes?
   - *Radial: 4 - 2 - 1 = 1. Angular: l = 2. Total: 3.*

2. Why can't l = 3 exist for n = 2?
   - *Total nodes = n - 1 = 1. But l = 3 requires 3 angular nodes. Not enough budget.*

3. Why does 4s fill before 3d in the building-up order?
   - *4s penetrates closer to nucleus, feels more Zeff, lower energy despite higher n.*

4. How many orbitals in the n = 4 shell? How many electrons max?
   - *Orbitals: n² = 16. Electrons: 2n² = 32.*

---

## Next

→ **Lesson 2: Electron Configuration** — Filling orbitals, building atoms
