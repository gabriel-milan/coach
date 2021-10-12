
import typer

from scoach.cli.utils import check_config
from scoach.logging import logger
from scoach.utils import (
    safe_object_get,
    get_minio_client,
    download_from_minio,
)

app = typer.Typer()


@app.command()
@logger.catch
def list():
    """
    List all scripts in the database.
    """
    if not check_config():
        return
    from scoach.models import Script
    scripts = Script.objects.all()
    if len(scripts) == 0:
        typer.echo("No scripts found.")
        return
    typer.echo(f"Found {len(scripts)} scripts.")
    for script in scripts:
        typer.echo(f"  - {script}")


@app.command()
@logger.catch
def download(script_id: str):
    """
    Downloads a script from the database.
    """
    if not check_config():
        return
    from scoach.models import Script
    script: Script = safe_object_get(Script, id=script_id)
    if script is None:
        typer.echo(f"Script {script_id} not found.")
        return
    typer.echo(f"Script {script_id} is available! Downloading...")
    minio_client = get_minio_client()
    download_from_minio(minio_client, script.path,
                        f"{script.id}.py")


@app.command()
@logger.catch
def delete(script_id: str):
    """
    Deletes a script from the database.
    """
    if not check_config():
        return
    from scoach.models import Script
    script: Script = safe_object_get(Script, id=script_id)
    if script is None:
        typer.echo(f"Script {script_id} not found.")
        return
    typer.echo(f"Script {script_id} will be deleted!")
    typer.echo(f"Information: {script}")
    choice = typer.prompt("Are you sure?", default=False,
                          show_choices=True, type=bool)
    if choice:
        script.delete()
        typer.echo(f"Script {script_id} deleted!")
    else:
        typer.echo("Script not deleted.")


@app.command()
@logger.catch
def describe(script_id: str):
    """
    Describes a script in the database.
    """
    if not check_config():
        return
    from scoach.models import Script, Run
    script: Script = safe_object_get(Script, id=script_id)
    if script is None:
        typer.echo(f"Script {script_id} not found.")
        return
    typer.echo(f"Script #{script_id}")
    typer.echo(f"  - Created at: {script.date_created}")
    typer.echo(f"  - Modified at: {script.date_modified}")
    typer.echo(f"  - Path: {script.path}")
    related_runs = Run.objects.filter(script=script)
    if len(related_runs) == 0:
        typer.echo("  - No runs found for this script.")
    else:
        typer.echo(f"  - {len(related_runs)} runs found for this script:")
        for run in related_runs:
            typer.echo(f"    * {run}")
    typer.echo()
