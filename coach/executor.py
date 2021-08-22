"""
Provides Executor, a wrapper for a Prefect Flow
"""

from time import sleep
from threading import Thread
from functools import partial

import jinja2
from prefect import task, Flow
from prefect.engine.state import State
from prefect.executors import DaskExecutor

from coach.constants import constants
from coach.db import DBManager
from coach.scheduler import Scheduler
from coach.job_config import JobConfig
from coach.logging import logger
from coach.utils import get_minio_client, load_env_as_type


@task
def render_template(template_text: str, **kwargs):
    """
    Task to render a jinja2 template

    Args:
        - template_text (str): the text of the template to render
        - **kwargs (dict): the keyword arguments to pass to the template

    Returns:
        - str: the rendered template
    """
    return jinja2.Template(template_text).render(**kwargs)


@task
def execute_template(rendered_template: str):
    """
    Task to execute a rendered template

    Args:
        - rendered_template (str): the rendered template to execute
    """
    # pylint: disable=exec-used
    exec(rendered_template)


# pylint: disable=too-few-public-methods
class Executor:
    """
    A wrapper for a Prefect Flow
    """

    def __init__(self, scheduler: Scheduler):
        self._scheduler = scheduler
        self._executor = DaskExecutor(scheduler.address)
        self._db: DBManager = DBManager()

    def _threaded_execution_handler(self, flow: Flow, job_config: JobConfig):
        """
        Threaded handler for the flow execution
        """
        self._db.update_run_status(
            job_config.run_id, constants.RUN_STATUS_RUNNING.value
        )
        state: State = flow.run(executor=self._executor)
        while not state.is_finished():
            sleep(0.25)
        if state.is_failed():
            self._db.update_run_status(
                job_config.run_id, constants.RUN_STATUS_FAILED.value
            )
            logger.error(f"Job {job_config.run_id} failed with error: {state.result}")
        elif state.is_successful():
            logger.info(f"Job {job_config.run_id} completed successfully")

    def execute(self, job_config: JobConfig, model_config: dict):
        """
        Execute the training job
        """
        job_config.params.update({"model_config": model_config})
        with Flow("Training Flow") as flow:
            minio_client = get_minio_client()
            bucket = load_env_as_type(
                constants.MINIO_BUCKET_ENV.value,
                default=constants.MINIO_BUCKET_ENV_DEFAULT.value,
            )
            script_path = self._db.get_script_path(job_config.script_key)
            template_text = (
                minio_client.get_object(bucket, script_path).read().decode("utf-8")
            )
            rendered_template = render_template(
                template_text,
                **job_config.params,
                **job_config._asdict(),
                **{"run_config": job_config._asdict()},
            )
            execute_template(rendered_template)

        thread = Thread(
            target=partial(self._threaded_execution_handler, flow, job_config),
            daemon=True,
        )
        thread.start()
