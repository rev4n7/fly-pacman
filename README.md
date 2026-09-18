# Fly-Pacman 🪰

**A Pac-Man game played by a fruit fly that nobody controls.** Its "brain" is a spiking neural network wired with **real synapses from the male fruit fly connectome** ([MaleCNS v1.0](https://www.janelia.org/project-team/flyem/male-cns-connectome), via [neuPrint](https://neuprint.janelia.org)).

![Fly-Pacman screenshot: maze, live fly brain, eye and escape panels](docs/screenshot.png)

- 🧠 **1,887 simulated neurons, 1.15 million real synapses.** Leaky integrate-and-fire neurons using the constants of a published whole-fly-brain model.
- 👀 **Looming detectors (LC4, LPLC2, LC6)** fire as a ghost charges, and they drive the **Giant Fiber**, the fly's real escape neuron.
- 🚫 **No `if ghost_near: run` rule.** The fly escapes only when its simulated Giant Fiber fires.
- 🟢 A visual pursuit pathway (**LC10a → AOTU → DNa02**) steers it toward pellets.
- ✨ **Live brain view:** every neuron glows at its **real position** in the fly's head, from 12.7 million synapse locations.

## Run it

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows  (macOS/Linux: source .venv/bin/activate)
pip install -r requirements.txt
python -m flypac.game
```

The connectome data the game needs is already in `data/`, so **no account is required to play.**

| Key | Action |
|---|---|
| `Space` | pause |
| `F` | fast-forward |
| `W` / `F11` | fullscreen |
| `+` / `-` | ghost speed |
| `1`–`4` | number of ghosts |
| `M` | escape readout: `eyes` / `circuit` |
| `H` | hearing on/off |
| `R` | restart |
| `S` | screenshot |

## How it works

```
maze scene ──► sensory neurons ──► 1.15M real synapses ──► descending neurons ──► fly movement
 (ghosts,       (LC4/LPLC2/LC6      (LIF network,            (Giant Fiber = jump,
  pellets,       looming, LC10a      0.1 ms steps)            DNa02 = steer)
  air)           pellets, JO ears)
```

1. **Data layer** (`flypac/fetch.py`): `neuprint-python` queries pull the escape, pursuit and hearing circuits.
   - Middlemen and feedback neurons are chosen by **synapse-count rules**, not hand-picked.
   - Each visual neuron's viewing direction comes from its real dendrite position in the lobula.
2. **Neuron sim** (`flypac/brain.py`): leaky integrate-and-fire neurons.
   - Weight = synapse count × 0.275 mV × sign, where the sign comes from the predicted neurotransmitter.
   - Constants follow Shiu et al. 2024.
3. **Game** (`flypac/world.py`, `flypac/maze.py`): maze, ghosts with classic chase AI, line of sight, and near-field "sound" along corridors.
4. **Display** (`flypac/game.py`, `flypac/brainview.py`): the maze, the live anatomical brain, the eye map, and the escape and steering gauges.

The full plain-English explanation, including every design decision, bug and fix, is in **[DEBRIEF.md](DEBRIEF.md)**. The lab notebook is in [`scoping/SCOPING.md`](scoping/SCOPING.md).

## What's real and what's a design choice

| Real connectome data | Design choices (tuned or invented) |
|---|---|
| which neurons exist; every connection and its synapse count | how strongly ghosts and pellets excite the sensory neurons |
| predicted neurotransmitter (excite/inhibit) | mapping neuron output to maze moves; jump speed |
| where each neuron sits and where each visual neuron looks | ghost "sound"; background wandering drive |
| brain and optic-lobe shapes | brain-view brightness (feedback neurons drawn dimmer) |

**Limitations**
- It's a circuit subset (1,887 of ~167k neurons).
- Synapse counts ≠ true synaptic strengths.
- Electrical synapses (e.g. Giant Fiber → jump muscle) are invisible in EM data.
- The right-ear wiring is mirrored from the better-traced left ear.
- Front/back escape direction is weakly encoded in the escape neurons, so the default readout uses the looming neurons.
- LC10a is a courtship-pursuit pathway, used here for pellets.

## Regenerating the data (optional)

Needs a free neuPrint account: sign in at [neuprint.janelia.org](https://neuprint.janelia.org), copy your token, and put it in a `.env` file:

```
NEUPRINT_APPLICATION_CREDENTIALS=your-token-here
```

Then:

```bash
python -m flypac.fetch            # circuit: neurons, connections, retinotopy
python -m flypac.fetch_anatomy    # brain shapes + synapse positions for the brain view
```

## Credits and data license

- **Connectome:** FlyEM Male CNS dataset (Janelia Research Campus FlyEM, Cambridge Drosophila Connectomics Group, Google Connectomics), licensed **[CC-BY 4.0](https://creativecommons.org/licenses/by/4.0/)**.
  - Files in `data/` are derived from it (synapse counts, positions, region shapes).
  - Please cite the dataset paper: [bioRxiv 10.1101/2025.10.09.680999](https://www.biorxiv.org/content/10.1101/2025.10.09.680999v2) / *Cell* (2026).
- **neuPrint** and **neuprint-python**: Janelia Research Campus.
- **Neuron model constants:** Shiu et al. (2024), *A Drosophila computational brain model reveals sensorimotor processing*, *Nature*.
- **Looming-neuron synaptic gradients:** Dombrovski et al. (2023), *Synaptic gradients transform object location to action*, *Nature*.
