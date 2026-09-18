"""Which neurons we pull from male-cns:v1.0, and why.

Core types are named explicitly (justified in scoping/SCOPING.md). Middle-layer
interneurons are NOT hand-picked: they are selected by synapse-count thresholds
applied to the real connectome in fetch.py.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
SERVER = "neuprint.janelia.org"
DATASET = "male-cns:v1.0"

# --- sensory populations (stimulus is injected here) ---
LOOMING_TYPES = ["LC4", "LPLC2", "LC6"]   # looming / approaching-object detectors
PURSUIT_TYPES = ["LC10a"]                  # small-object pursuit (courtship chase) detectors
HEARING_PREFIX = "JO"                      # Johnston's organ: antenna sound / air-vibration sensors

# --- descending / motor readouts ---
ESCAPE_TYPES = ["DNp01", "DNp02", "DNp04", "DNp06", "DNp11", "TTMn", "PSI"]  # DNp01 = Giant Fiber
STEER_TYPES = ["DNa02", "DNa03", "DNa01", "DNp09"]

# --- middle-layer selection thresholds (synapse counts, per middle cell) ---
GF_MID_MIN_IN = 100    # >= this many synapses from looming/hearing sensors ...
GF_MID_MIN_OUT = 50    # ... and >= this many onto a Giant Fiber
STEER_MID_MIN_IN = 100   # >= from LC10a ...
STEER_MID_MIN_OUT = 100  # ... and >= onto DNa02/DNa03
# feedback layer: ANY neuron (any transmitter) receiving >= IN synapses from the circuit and
# sending >= OUT synapses back onto its middle/output neurons. Restores the local balance
# (mostly inhibition) that a bare feed-forward selection throws away.
FEEDBACK_MIN_IN = 100
FEEDBACK_MIN_OUT = 100
JO_MIN_OUT = 5         # JO cell kept if it sends >= this many synapses into the circuit

# --- synapse sign from predicted neurotransmitter ---
# Same convention as the Shiu et al. 2024 whole-brain LIF model: ACh excitatory,
# GABA and glutamate inhibitory (fly CNS glutamate mostly acts via GluCl).
# Modulatory / unclear transmitters get sign 0 (not modelled as fast synapses).
NT_SIGN = {"acetylcholine": 1, "gaba": -1, "glutamate": -1}

# --- eye geometry (approximate literature values, NOT connectome data) ---
# Per-eye azimuth coverage in degrees: 0 = straight ahead, positive = toward that
# eye's side, 180 = straight behind. Frontal edge crosses the midline (binocular
# overlap); the rear edge leaves a blind spot behind the fly.
AZ_FRONT, AZ_BACK = -15.0, 160.0
EL_BOTTOM, EL_TOP = -60.0, 60.0
