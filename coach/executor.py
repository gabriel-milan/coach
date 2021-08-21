import jinja2
from minio import Minio
from prefect import task, Flow
from prefect.executors import DaskExecutor

from coach.constants import constants
from coach.scheduler import Scheduler
from coach.job_config import JobConfig
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
    exec(rendered_template)


class Executor(object):

    def __init__(self, scheduler: Scheduler):
        self._scheduler = scheduler
        self._executor = DaskExecutor(scheduler.address)

    def execute(self, job_config: JobConfig, model_config: dict):
        """
        Execute the training job
        """
        job_config.params.update({"model_config": model_config})
        with Flow("Training Flow") as flow:
            minio_client = get_minio_client()
            bucket = load_env_as_type(constants.MINIO_BUCKET_ENV.value,
                                      default=constants.MINIO_BUCKET_ENV_DEFAULT.value)
            template_text = minio_client.get_object(
                bucket, job_config.script_key).read().decode("utf-8")
            rendered_template = render_template(
                template_text, **job_config.params, **job_config._asdict())
            execute_template(rendered_template)
        flow.run(executor=self._executor)
