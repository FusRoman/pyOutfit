# Request parallel execution when supported by the build
from py_outfit import IODParams

params = (
    IODParams.builder()
    .do_parallel()    # advisory flag consumed by higher-level APIs
    .batch_size(8)  # number of trajectories to schedule at once
    .build()
)
print(params.do_parallel, params.batch_size)
