"""
Provides Coach, the main class for the application.
"""

import json
import uuid
from os.path import join

from coach.constants import constants
from coach.db import DBManager
from coach.executor import Executor
from coach.job_config import JobConfig
from coach.logging import logger
from coach.pubsub import Broker
from coach.scheduler import Scheduler
from coach.utils import get_minio_client, load_env_as_type, save_to_minio


class Coach:
    """
    Main class for Coach
    """

    def __init__(self):
        logger.info("Coach instance initializing...")
        self._db: DBManager = None
        self._broker: Broker = None
        self._scheduler: Scheduler = None
        self._executor: Executor = None

    def _initialize_db(self):
        logger.info("Starting DBManager instance...")
        self._db: DBManager = DBManager()
        logger.info("DBManager instance started successfully!")

    def _initialize_broker(self):
        logger.info("Starting Broker instance...")
        self._broker: Broker = Broker()
        logger.info("Broker instance started successfully!")

    def _initialize_scheduler(self):
        logger.info("Starting Scheduler instance...")
        self._scheduler: Scheduler = Scheduler()
        logger.info("Scheduler instance started successfully!")

    def _initialize_executor(self):
        logger.info("Starting Executor instance...")
        if not self._scheduler:
            self._initialize_scheduler()
        self._executor: Executor = Executor(self._scheduler)
        logger.info("Executor instance started successfully!")

    @logger.catch
    def _message_handler(self, message):
        """
        Message handler for broker
        :param message:
        :return:
        """
        logger.info(f"Received message: {message}")
        if message["type"] == "message":
            data = json.loads(message["data"].decode("utf-8"))
            if not self._scheduler:
                self._initialize_scheduler()
            if not "job_config" in data:
                raise Exception("Job config not found")
            if not "model_config" in data:
                raise Exception("Model config not found")
            job_config = JobConfig(**data["job_config"])
            model_config = f'\'{json.dumps(data["model_config"])}\''
            if not self._executor:
                self._initialize_executor()
            self._executor.execute(job_config, model_config)

    @logger.catch
    def start_scheduler(self, redis_queue_name: str = None):
        """
        Starts the Coach daemon
        :param redis_queue_name:
        :return:
        """
        if not self._scheduler:
            self._initialize_scheduler()
        if not self._executor:
            self._initialize_executor()
        redis_queue_name = redis_queue_name or load_env_as_type(
            constants.REDIS_QUEUE_NAME_ENV.value,
            default=constants.REDIS_QUEUE_NAME_ENV_DEFAULT.value,
        )
        logger.info(
            f'Starting Redis queue consumer for queue_name="{redis_queue_name}"...'
        )
        self._initialize_broker()
        self._broker.run_in_thread(redis_queue_name, self._message_handler)
        logger.info("Redis queue consumer started successfully!")
        logger.info("Coach daemon is executing...")

    @logger.catch
    def submit_job(
        self,
        python_script_path: str,
        job_config: dict,
        model_config: dict,
        redis_queue_name: str = None,
    ) -> str:
        """
        Submits a job to the broker
        """
        # Generate unique path for python script
        script_id = str(uuid.uuid4())
        minio_script_path = join(
            constants.SCRIPTS_PATH_PREFIX.value,
            script_id,
            python_script_path.split("/")[-1],
        )
        if not self._db:
            self._initialize_db()
        self._db.add_script(script_id, minio_script_path)
        # Upload script to MinIO
        minio_client = get_minio_client()
        save_to_minio(minio_client, minio_script_path, python_script_path)
        # Generate unique job id
        job_id = str(uuid.uuid4())
        # Set job config with MinIO script path and run_id
        job_config["run_id"] = job_id
        job_config["script_key"] = script_id
        # Add job to the database
        self._db.create_empty_run(job_id)
        # Submit job
        redis_queue_name = redis_queue_name or load_env_as_type(
            constants.REDIS_QUEUE_NAME_ENV.value,
            default=constants.REDIS_QUEUE_NAME_ENV_DEFAULT.value,
        )
        logger.info(
            f'Submitting job with id="{job_id}" to Redis queue="{redis_queue_name}"...'
        )
        if not self._broker:
            self._initialize_broker()
        payload = {"job_config": job_config, "model_config": model_config}
        self._broker.publish(redis_queue_name, json.dumps(payload))
        return job_id
