"""
Provides scoach, the main class for the application.
"""

import json
import uuid
import time
from os.path import join
from threading import Thread

from scoach.constants import constants
from scoach.executor import Executor
from scoach.logging import logger
from scoach.scheduler import Scheduler
from scoach.utils import get_minio_client, load_env_as_type, save_to_minio


class Scoach:
    """
    Main class for scoach
    """

    def __init__(self):
        logger.info("scoach instance initializing...")
        self._scheduler: Scheduler = None
        self._executor: Executor = None
        self._scheduler_thread: Thread = None

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

    def _initialize_scheduler_thread(self):
        logger.info("Starting Scheduler thread...")
        self._scheduler_thread = Thread(target=self._threaded_scheduler)
        self._scheduler_thread.start()
        logger.info("Scheduler thread started successfully!")

    @logger.catch
    def _threaded_scheduler(self):
        """
        Constantly checks for new runs
        and launches them
        :return:
        """
        from scoach.models import Run
        while True:
            try:
                new_runs = Run.objects.all().filter(
                    status__status=constants.RUN_STATUS_CREATED.value)
                for run in new_runs:
                    logger.info(f"Sending new run ({run}) to the executor")
                    if not self._scheduler:
                        self._initialize_scheduler()
                    if not self._executor:
                        self._initialize_executor()
                    self._executor.execute(run.id)
            except Exception as e:
                logger.error(f"Error in scheduler: {e}")
            finally:
                logger.info(
                    f"Scheduler sleeping for {constants.SCHEDULER_SLEEP_TIME.value} seconds")
                time.sleep(constants.SCHEDULER_SLEEP_TIME.value)

    @logger.catch
    def start_scheduler(self):
        """
        Starts the scoach daemon
        :return:
        """
        if not self._scheduler:
            self._initialize_scheduler()
        if not self._executor:
            self._initialize_executor()
        logger.info("Starting scheduler in a thread...")
        self._initialize_scheduler_thread()
        logger.info("scoach daemon is executing...")
