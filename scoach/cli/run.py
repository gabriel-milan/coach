"""
Provides CLI app for scoach.
"""

import json
from typing import List
import uuid
from pathlib import Path
from os.path import join

import typer

from scoach.cli.utils import check_config
from scoach.constants import constants
from scoach.logging import logger
from scoach.utils import (
    get_minio_client,
    save_to_minio,
    safe_object_get
)

app = typer.Typer()


@app.command()
@logger.catch
def submit(python_script: Path, job_config: Path, model_config: Path, tags: List[str] = None):
    """
    Submits a job to the queue.
    """
    if not check_config():
        return
    from scoach.models import Script, Parameters, Model, Status, Run, Tag
    # Check if all paths exists
    if not python_script.exists():
        script: Script = safe_object_get(Script, id=str(python_script))
        if script is None:
            typer.echo(
                "Python script does not exist locally and was not found on database."
            )
            return
    else:
        script_id = str(uuid.uuid4())
        minio_script_path = join(
            constants.SCRIPTS_PATH_PREFIX.value,
            script_id,
            str(python_script).split("/")[-1],
        )
        script: Script = Script.objects.create(
            path=minio_script_path
        )
        save_to_minio(get_minio_client(),
                      minio_script_path, str(python_script))
        script.save()
    if not job_config.exists():
        typer.echo("Job config does not exist.")
        return
    if not model_config.exists():
        typer.echo("Model config does not exist.")
        return
    # Load job_config json
    # pylint: disable=invalid-name
    with job_config.open() as f:
        job_config = json.load(f)
    parameters: Parameters = safe_object_get(
        Parameters, config=json.dumps(job_config))
    if parameters is None:
        parameters = Parameters.objects.create(config=json.dumps(job_config))
        parameters.save()
    # Load model_config json
    # pylint: disable=invalid-name
    with model_config.open() as f:
        model_config = json.load(f)
    model: Model = safe_object_get(Model, config=json.dumps(model_config))
    if model is None:
        model = Model.objects.create(config=json.dumps(model_config))
    model.save()
    # Submit job
    status: Status = safe_object_get(
        Status, status=constants.RUN_STATUS_CREATED.value)
    if status is None:
        status = Status.objects.create(
            status=constants.RUN_STATUS_CREATED.value)
        status.save()
    run: Run = Run.objects.create(
        model=model,
        script=script,
        parameters=parameters,
        status=status,
    )
    run.save()
    if tags is not None:
        for tag in tags:
            tag_obj: Tag = safe_object_get(Tag, name=tag)
            if tag_obj is None:
                tag_obj: Tag = Tag.objects.create(name=tag)
                tag_obj.save()
            run.tags.add(tag_obj)
        run.save()
    typer.echo(f"Submitted run with id {run.id}")


# pylint: disable=redefined-builtin
@app.command()
@logger.catch
def list():
    """
    List all jobs.
    """
    if not check_config():
        return
    from scoach.models import Run
    runs = Run.objects.all()
    typer.echo(f"Found {len(runs)} runs.")
    for run in runs:
        typer.echo(f"  - {run}")


@app.command()
@logger.catch
def delete(run_id: str):
    """
    Deletes a run from the database.
    """
    if not check_config():
        return
    from scoach.models import Run
    run: Run = safe_object_get(Run, id=run_id)
    if run is None:
        typer.echo(f"Run {run_id} not found.")
        return
    typer.echo(f"Run {run_id} will be deleted!")
    typer.echo(f"Information: {run}")
    choice = typer.prompt("Are you sure?", default=False,
                          show_choices=True, type=bool)
    if choice:
        run.delete()
        typer.echo(f"Run {run_id} deleted!")
    else:
        typer.echo("Run not deleted.")


@app.command()
@logger.catch
def describe(run_id: str):
    """
    Describes a run from the database.
    """
    if not check_config():
        return
    from scoach.models import Run
    run: Run = safe_object_get(Run, id=run_id)
    if run is None:
        typer.echo(f"Run {run_id} not found.")
        return
    typer.echo(f"Run #{run_id}")
    typer.echo(f"  - Status: {run.status}")
    typer.echo(f"  - Train score: {run.train_score}")
    typer.echo(f"  - Validation score: {run.validation_score}")
    typer.echo(f"  - Created at: {run.date_created}")
    typer.echo(f"  - Modified at: {run.date_modified}")
    typer.echo(f"  - Model: {run.model}")
    typer.echo(f"  - Script: {run.script}")
    typer.echo(f"  - Parameters: {run.parameters}")
    typer.echo(f"  - Tags: {[t.name for t in run.tags.all()]}")
    typer.echo()
    typer.echo(
        "If you desire to load this model, open a Python shell and do the following:"
    )
    typer.echo(">>> from scoach.utils import load_run")
    typer.echo(f">>> model = load_run({run_id})")


@app.command()
@logger.catch
def retry(run_id: str):
    """
    Retries a run.
    """
    if not check_config():
        return
    from scoach.models import Status, Run
    run: Run = safe_object_get(Run, id=run_id)
    if run is None:
        typer.echo(f"Run {run_id} not found.")
        return
    if run.status.status != constants.RUN_STATUS_FAILED.value:
        typer.echo(f"Run {run_id} is not in failed status.")
        return
    status: Status = safe_object_get(
        Status, status=constants.RUN_STATUS_CREATED.value)
    if status is None:
        status = Status.objects.create(
            status=constants.RUN_STATUS_CREATED.value)
        status.save()
    run.status = status
    run.save()
    typer.echo(f"Run {run_id} retried!")
