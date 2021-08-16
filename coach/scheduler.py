from dask_jobqueue import SLURMCluster

from coach.constants import constants
from coach.utils import load_env_as_type


class Scheduler(object):
    def __init__(self, partition=None, cores=None, memory=None, name=None, exclusive=None, max_workers=None):
        partition = partition or load_env_as_type(
            constants.SLURM_PARTITION_ENV.value, default=constants.SLURM_PARTITION_ENV_DEFAULT.value)
        cores = cores or load_env_as_type(
            constants.SLURM_CORES_PER_JOB_ENV.value, int, default=constants.SLURM_CORES_PER_JOB_ENV_DEFAULT.value)
        memory = memory or load_env_as_type(
            constants.SLURM_MEMORY_PER_JOB_ENV.value, default=constants.SLURM_MEMORY_PER_JOB_ENV_DEFAULT.value)
        name = name or load_env_as_type(
            constants.SLURM_WORKER_NAME_ENV.value, default=constants.SLURM_WORKER_NAME_ENV_DEFAULT.value)
        exclusive = exclusive or load_env_as_type(
            constants.SLURM_JOB_EXCLUSIVE_ENV.value, bool, default=constants.SLURM_JOB_EXCLUSIVE_ENV_DEFAULT.value)
        max_workers = max_workers or load_env_as_type(
            constants.SLURM_MAX_WORKERS_ENV.value, int, default=constants.SLURM_MAX_WORKERS_ENV_DEFAULT.value)
        job_extra = ["--exclusive"] if exclusive else []
        self._cluster = SLURMCluster(
            queue=partition,
            cores=cores,
            memory=memory,
            name=name,
            job_extra=job_extra,
        )
        self._cluster.scale(jobs=constants.DASK_DEFAULT_WORKERS.value)
        self._cluster.adapt(maximum_jobs=max_workers)
        self._cluster.start()

    @property
    def address(self):
        return self._cluster.scheduler.address

    def close(self):
        self._cluster.close()
