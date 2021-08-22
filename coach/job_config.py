"""
A namedtuple wrapper for a job config
"""

from collections import namedtuple

JobConfig = namedtuple("JobConfig", ["run_id", "script_key", "params",])
