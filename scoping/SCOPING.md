# Fly-Pacman — connectome scoping (male-cns:v1.0)

Queried 2026-09-16 against https://neuprint.janelia.org, dataset `male-cns:v1.0`.
Scoping used anonymous HTTP (`rawq.py`); the real data layer will use neuprint-python (needs token).
Raw long-format edge list: `scope_matrix_long.csv` (regenerate with `matrix.py`).

## Escape pathway (all ipsilateral, all real chemical synapses)

| pre → post | L side | R side | pre NT |
|---|---|---|---|
| LC4 → GF (DNp01) | 3782 (71 cells) | 2580 (55 cells) | ACh |
| LPLC2 → GF | 2642 (94) | 2220 (91) | ACh |
| LC6 → PVLP151 (same side) | 1123 | 1556 | ACh |
| PVLP151 → GF (**contralateral**) | 256 (L→GF_R) | 326 (R→GF_L) | ACh |
| LPLC2 → PVLP151 | 3265 | 3164 | ACh |
| LC4 → DNp11 | 2022 | 1644 | ACh |
| GF → TTMn (jump MN) | **20** | **70** | ACh |
| GF → PSI | 9 / 2 | 2 / 3 | ACh |

- LC6 does NOT synapse on GF directly; it reaches GF only via PVLP151 (2 hops).
- Large within-type recurrence (LC4→LC4 ~11k, LPLC2→LPLC2 ~24k synapses) — must be normalized in the sim or it runs away.

## Approach / steering pathway (LC10a visual pursuit → DNa02 steering)

| pre → post | L | R | NT |
|---|---|---|---|
| LC10a → AOTU019 | 6615 | 7595 | ACh |
| AOTU019 → DNa02 (contra) | 289 | 297 | **GABA** (inhibits opposite side) |
| LC10a → AOTU012/015/025 | ~2-3.5k each | ~2.4-3.7k | ACh |
| AOTU012/015/025 → DNa02 (ipsi) | 218/291/205 | 164/281/196 | ACh |
| AOTU001 → DNa02 (contra) | 214 | 208 | ACh |
| DNa03 → DNa02 (ipsi) | 255 | 297 | ACh |

No meaningful direct synapses between the escape and approach sets (no LC4/GF → DNa02).

## Limitations of the public data

1. **Gap junctions are invisible in EM.** GF→TTMn and GF→PSI are mainly electrical synapses
   in the real fly, so their chemical counts are tiny and L/R asymmetric (20 vs 70).
2. Synapse count ≠ synaptic strength. Sign comes from *predicted* NT (ACh +, GABA −;
   glutamate is ambiguous in flies). A global gain is an unavoidable free parameter.
3. LC10a is a pursuit pathway (males chasing moving targets), not a food-seeking circuit.
4. Sensory transduction (photoreceptors → lobula) is not simulated; stimulus is injected into LC cells.
5. Per-cell retinotopy is available (lobula dendrite centroids, ~4 s query), but mapping
   position → azimuth requires a fitted axis, not a connectome value.

## Decisions (2026-09-16)
1. GF spike = jump command (no invented gap-junction weights). TTMn shown with real chemical weights only.
2. LC10a pursuit pathway used for pellet approach (caveat disclosed).
3. Maze makes front/back threat direction matter → per-cell retinotopy is needed (see below).

## Threat-direction wiring (direction_check.py, neuprint-python with token)
Per-cell synapse counts from looming cells onto descending neurons vary systematically with where
each cell's dendrites sit in the lobula (= where in the visual field it looks):
- LC4 → DNp02 vs LC4 → DNp11: opposite gradients along the same axis (|r| 0.72–0.88, both sides).
- LC4 → DNp04: gradient along the other axis (r ≈ -0.66, both sides).
- LPLC2 → GF: gradient (r ≈ -0.71 / -0.79).
PCA axis signs are arbitrary; which end is front/back/up/down still has to be anchored anatomically.
Consistent with published synaptic-gradient findings (Dombrovski et al. 2023), to be cross-checked.

## Hearing / air-vibration input to GF (Johnston's organ, JO)
- Direct JO → GF: GF_L 679 syn (mostly JO-B1_a 518, JO-B1_c 146); GF_R only 30. JO cells have no
  somaSide and the asymmetry is likely a tracing/typing artifact of cut-off sensory axons. JO→GF is also
  known to be partly electrical (ShakB) → invisible, like GF→TTMn.
- Indirect JO → SAD/GNG interneurons → GF: mix of excitatory (SAD064, SAD053; ACh) and inhibitory
  (SAD107, SAD103, SAD109, SAD111, GNG300; GABA). Hearing can both push and brake the GF.
- Looming input to GF is ~7-10x larger than direct hearing input.

## Decision 4 (2026-09-16): blind spot = C + D
Realistic rear blind spot, eyes + hearing (JO), difficulty tuned via ghost speed.

## Data layer v1 (flypac/fetch.py → data/)
- 1155 neurons, 45,313 connections, 283,360 synapses. Middle layers selected by thresholds (config.py).
- Front/back anchor: dataset z = posterior, y = ventral, x = fly's left (AL vs calyx, HSN vs HSS).
  Tm1 shows medulla→lobula front/back flip (r = -0.97 R, -0.94 L); dorsal/ventral preserved (r = 1.00).
  Lamina→medulla flip taken from textbook anatomy (lamina not testable here).
- Gradients in visual-field terms (both sides agree): LC4→DNp02 front-biased (r -0.63/-0.73),
  LC4→DNp11 rear+dorsal (+0.50), LC4→DNp04 ventral (-0.66), LPLC2→GF dorsal (+0.69/+0.75).
- Hearing asymmetry: JO cells 243 L vs 101 R; JO→GF direct 679 (L) vs 29 (R). Tracing artifact, unresolved.
- Input coverage of outputs by our subset: GF 61-65%, DNp02 44-54%, DNp11 30-32%, DNa02 5-6%, TTMn 2-4%.

## Progress log — end of day 2026-09-16
- Decision 5: hearing = option B (right ear mirrored from real left-ear wiring; brain.py mirror_hearing).
- Data layer v2: added feedback layer (any NT, >=100 in from circuit and >=100 out back) → 1745 neurons,
  ~1.1M synapses. This alone stopped runaway activity; ADAPT_B can likely be set to 0 (currently 2.0 in brain.py).
- Brain (LIF, Shiu et al. 2024 constants) runs ~real time. Standalone tests (flypac/test_brain.py):
  pellets steer correctly L/R; blind spot works (rear ghost noticed at ~1 tile, eyes only).
- Vision gain: loom_half ≈ 1500 → jump at ~1.4–2.1 tiles for a 4 tiles/s ghost; sideways pass ignored.
- Escape direction (scoping/direction_eval.py): LEFT/RIGHT 95–100% correct. FRONT/BACK only 48–65%
  with rule DNp11−DNp02 (biased to "forward"; DNp11 also driven by GF itself).
- TODO next: (1) test if front/back info exists at all in output neurons (scoping/decode_info.py, not yet run;
  needs `pip install scikit-learn`); (2) hearing gain is far too strong (jumps at 6–9 tiles) — make near-field
  steeper; (3) then game shell → wiring together.

## Progress log — 2026-09-17
- Front/back info test (scoping/decode_info.py): looming sensors 100%, escape DNs 59%, DNs+middle 68%
  (held-out bearings). Scan of all DNs: front/back gradients weak once LC4+LPLC2+LC6 combined (DNp05 most
  frontal, 74% front input). Conclusion: real limitation at the DN level in this data/model.
- Hearing now near-field (speed*(r0/d)^3, threshold). Real wiring makes hearing net-INHIBITORY on GF
  (GABA SAD/GNG middlemen); excitatory JO->GF partly electrical in reality (invisible) -> flagged.
- ADAPT_B = 0 (feedback layer balances network). Brain optimized: ~6x real time.
- Game built: flypac/maze.py, world.py (logic), game.py (pygame + brain panel).
- Batch (scoping/batch.py, 120 s x 3 seeds): 'eyes' readout survives 45-64% of jumps, caught 5-6/2min;
  'circuit' readout 14-24%, caught 10-12/2min. Hearing on/off: no consistent effect.
- OPEN DECISION for user: default front/back readout (circuit vs eyes).

## Fix round — 2026-09-17 (user: "fly dumb, ghost U-turn kills it")
- Diagnosis (scoping/catch_causes.py, uturn.py): brain fires GF 80-500 ms before contact; NOT a brain delay.
  Causes: (1) 'circuit' readout jumped toward ghost in ~38% of takeoffs; (2) game bug: 0.85 s jump cooldown
  ignored repeated GF spikes (trace at t=73.5-74.1, seed 1); (3) ~75% of remaining catches are sandwiches
  by a different ghost in the blind spot (scoping/sandwich.py).
- Fixes: JUMP_COOLDOWN 0, COMMIT_DELAY 0, default readout 'eyes', default ghost speed 2.0 (option C).
  Result at 2.0: ~1 catch / 45 s, ~32 jumps / 3 min, toward-ghost takeoffs ~1%.

## Brain view — 2026-09-17
- flypac/fetch_anatomy.py: ROI meshes (CentralBrain, LO/LOP/ME/LA L+R) -> filled silhouettes; all synapse
  locations of 1745 neurons binned to 400-voxel pixels (12.74M synapses). rand() sampling in Cypher returned
  all-or-nothing per batch -> removed. View from behind (screen x = -dataset x).
- flypac/brainview.py: per-neuron footprint sparse matrix x firing rate -> RGB glow. Display: gain 0.25,
  WEIGHT_POW 0.7, feedback cells 45% brightness (labelled). Caption + 6 s trace.
- Performance: frame 30 ms -> ~20 ms (vectorised panel colours, small blind-spot overlay, batched Poisson draws
  + bincount in brain.step, LOS cache, glow at 25 fps). Behaviour re-verified (sandwich.py, uturn.py).
