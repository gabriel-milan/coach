import json
import uuid
from os.path import join

from coach.constants import constants
from coach.db import DBManager
from coach.executor import Executor
from coach.job_config import JobConfig
from coach.pubsub import Broker
from coach.scheduler import Scheduler
from coach.utils import get_minio_client, load_env_as_type


class Coach(object):
    """
    Main class for Coach
    """

    def __init__(self):
        self._broker: Broker = Broker()
        self._db: DBManager = DBManager()
        self._scheduler: Scheduler = None
        self._executor: Executor = None

    def _message_handler(self, message):
        """
        Message handler for broker
        :param message:
        :return:
        """
        if message["type"] == "message":
            data = json.loads(message["data"].decode("utf-8"))
            if not self._scheduler:
                raise Exception("Scheduler not started")
            if not "job_config" in data:
                raise Exception("Job config not found")
            if not "model_config" in data:
                raise Exception("Model config not found")
            job_config = JobConfig(data["job_config"])
            model_config = data["model_config"]
            self._executor.execute(job_config, model_config)
        self._broker.publish(message)

    def start_scheduler(self, redis_queue_name: str = None):
        print("Starting Dask scheduler...", end="")
        self._scheduler = Scheduler()
        print(" success!")
        print("Starting Prefect executor...", end="")
        self._executor = Executor(self._scheduler)
        print(" success!")
        print("Starting Redis queue consumer...", end="")
        redis_queue_name = redis_queue_name or load_env_as_type(
            constants.REDIS_QUEUE_NAME_ENV.value, default=constants.REDIS_QUEUE_NAME_ENV_DEFAULT.value)
        self._broker.run_in_thread(redis_queue_name, self._message_handler)
        print(" success!")
        print("Coach daemon is executing.")

    def submit_job(self, python_script_path: str, job_config: dict, model_config: dict, redis_queue_name: str = None) -> str:
        # Generate unique path for python script
        minio_script_path = join(
            constants.SCRIPTS_PATH_PREFIX.value, str(uuid.uuid4()), python_script_path.split('/')[-1])
        # Upload script to MinIO
        minio_client = get_minio_client()
        minio_client.fput_object(
            load_env_as_type(constants.MINIO_BUCKET_ENV.value,
                             default=constants.MINIO_BUCKET_ENV_DEFAULT.value),
            minio_script_path, python_script_path)
        # Generate unique job id
        job_id = str(uuid.uuid4())
        # Set job config with MinIO script path and run_id
        job_config["run_id"] = job_id
        job_config["script_key"] = minio_script_path
        # Submit job
        redis_queue_name = redis_queue_name or load_env_as_type(
            constants.REDIS_QUEUE_NAME_ENV.value, default=constants.REDIS_QUEUE_NAME_ENV_DEFAULT.value)
        return job_id
