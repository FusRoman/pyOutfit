# Control the RMS evaluation window and triplet spacing
from py_outfit import IODParams

params = (
    IODParams.builder()
    .extf(2.0)              # scale relative to triplet span
    .dtmax(45.0)            # floor in days for evaluation window
    .dt_min(0.05)           # shortest allowed triplet span
    .dt_max_triplet(120.0)  # longest allowed triplet span
    .optimal_interval_time(15.0)
    .max_triplets(50)
    .gap_max(6.0/24.0)
    .build()
)
print(params.extf, params.dtmax, params.max_triplets)
