from collections import namedtuple

JobConfig = namedtuple(
    'JobConfig', [
        'run_id',
        'script_key',
        'params',
    ]
)
