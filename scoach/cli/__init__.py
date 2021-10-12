from pathlib import Path

import yaml
import typer

from scoach.cli import run, script
from scoach.cli.utils import (
    check_config,
    check_database_exists,
    check_minio_connection,
)
from scoach.scoach import Scoach
from scoach.constants import constants
from scoach.logging import logger
from scoach.utils import setup_database

app = typer.Typer()
app.add_typer(run.app, name="run", help="Manages runs")
app.add_typer(script.app, name="script", help="Manages scripts")


@app.command()
@logger.catch
def init():  # pylint: disable=too-many-locals
    """
    Initialize (or override) configuration file.
    """
    # DB_HOST: "postgres"
    # DB_PORT: 5432
    # DB_USER: "postgres"
    # DB_PASSWORD: "postgres"
    # DB_NAME: "scoach"
    # SLURM_PARTITION: "debug"
    # SLURM_CORES_PER_JOB: 1
    # SLURM_MEMORY_PER_JOB: "1G"
    # SLURM_WORKER_NAME: "worker_name"
    # SLURM_JOB_EXCLUSIVE: false
    # SLURM_MAX_WORKERS: 1
    # MINIO_ENDPOINT: "minio.example.com"
    # MINIO_ENDPOINT_SCHEMA: "https"
    # MINIO_ENDPOINT_PORT: 443
    # MINIO_ACCESS_KEY: "minio_access_key"
    # MINIO_SECRET_KEY: "minio_secret_key"
    # MINIO_BUCKET: "minio_bucket_name"
    typer.echo(
        "Welcome to scoach! Please fill all requested fields!")
    db_host = typer.prompt(constants.DB_HOST_ENV.value,
                           default=constants.DB_HOST_ENV_DEFAULT.value)
    db_port = typer.prompt(constants.DB_PORT_ENV.value,
                           default=constants.DB_PORT_ENV_DEFAULT.value)
    db_user = typer.prompt(constants.DB_USER_ENV.value,
                           default=constants.DB_USER_ENV_DEFAULT.value)
    db_password = typer.prompt(
        constants.DB_PASSWORD_ENV.value, default=constants.DB_PASSWORD_ENV_DEFAULT.value)
    db_name = typer.prompt(constants.DB_NAME_ENV.value,
                           default=constants.DB_NAME_ENV_DEFAULT.value)

    typer.echo("Checking database connection...")
    if check_database_exists(db_host, db_port, db_user, db_password, db_name):
        typer.echo("Database connection successful!")
    else:
        typer.echo(
            "Database connection failed, please check your inputs or create database if needed.")
        return

    slurm_partition = typer.prompt(
        constants.SLURM_PARTITION_ENV.value, default=constants.SLURM_PARTITION_ENV_DEFAULT.value)
    slurm_cores_per_job = typer.prompt(
        constants.SLURM_CORES_PER_JOB_ENV.value, default=constants.SLURM_CORES_PER_JOB_ENV_DEFAULT.value)
    slurm_memory_per_job = typer.prompt(
        constants.SLURM_MEMORY_PER_JOB_ENV.value, default=constants.SLURM_MEMORY_PER_JOB_ENV_DEFAULT.value)
    slurm_worker_name = typer.prompt(
        constants.SLURM_WORKER_NAME_ENV.value, default=constants.SLURM_WORKER_NAME_ENV_DEFAULT.value)
    slurm_job_exclusive = typer.confirm(
        constants.SLURM_JOB_EXCLUSIVE_ENV.value, default=constants.SLURM_JOB_EXCLUSIVE_ENV_DEFAULT.value)
    slurm_max_workers = typer.prompt(
        constants.SLURM_MAX_WORKERS_ENV.value, default=constants.SLURM_MAX_WORKERS_ENV_DEFAULT.value)

    minio_endpoint = typer.prompt(
        constants.MINIO_ENDPOINT_ENV.value, default=constants.MINIO_ENDPOINT_ENV_DEFAULT.value)
    minio_endpoint_schema = typer.prompt(
        constants.MINIO_ENDPOINT_SCHEMA_ENV.value, default=constants.MINIO_ENDPOINT_SCHEMA_ENV_DEFAULT.value)
    minio_endpoint_port = typer.prompt(
        constants.MINIO_ENDPOINT_PORT_ENV.value, default=constants.MINIO_ENDPOINT_PORT_ENV_DEFAULT.value)
    minio_access_key = typer.prompt(
        constants.MINIO_ACCESS_KEY_ENV.value, default=constants.MINIO_ACCESS_KEY_ENV_DEFAULT.value)
    minio_secret_key = typer.prompt(
        constants.MINIO_SECRET_KEY_ENV.value, default=constants.MINIO_SECRET_KEY_ENV_DEFAULT.value)
    minio_bucket = typer.prompt(
        constants.MINIO_BUCKET_ENV.value, default=constants.MINIO_BUCKET_ENV_DEFAULT.value)

    typer.echo("Checking MinIO connection...")
    if check_minio_connection(minio_endpoint, minio_access_key, minio_secret_key, minio_bucket):
        typer.echo("MinIO connection successful!")
    else:
        typer.echo(
            "MinIO connection failed, please check your inputs or create bucket if needed.")
        return

    # Save configs to YAML file
    config_path = Path(constants.SCOACH_DEFAULT_CONFIG_PATH.value)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        yaml.dump(
            {
                constants.DB_HOST_ENV.value: db_host,
                constants.DB_PORT_ENV.value: db_port,
                constants.DB_USER_ENV.value: db_user,
                constants.DB_PASSWORD_ENV.value: db_password,
                constants.DB_NAME_ENV.value: db_name,
                constants.SLURM_PARTITION_ENV.value: slurm_partition,
                constants.SLURM_CORES_PER_JOB_ENV.value: slurm_cores_per_job,
                constants.SLURM_MEMORY_PER_JOB_ENV.value: slurm_memory_per_job,
                constants.SLURM_WORKER_NAME_ENV.value: slurm_worker_name,
                constants.SLURM_JOB_EXCLUSIVE_ENV.value: slurm_job_exclusive,
                constants.SLURM_MAX_WORKERS_ENV.value: slurm_max_workers,
                constants.MINIO_ENDPOINT_ENV.value: minio_endpoint,
                constants.MINIO_ENDPOINT_SCHEMA_ENV.value: minio_endpoint_schema,
                constants.MINIO_ENDPOINT_PORT_ENV.value: minio_endpoint_port,
                constants.MINIO_ACCESS_KEY_ENV.value: minio_access_key,
                constants.MINIO_SECRET_KEY_ENV.value: minio_secret_key,
                constants.MINIO_BUCKET_ENV.value: minio_bucket,
                constants.DJANGO_SETTINGS_MODE_ENV.value: constants.DJANGO_SETTINGS_MODE_ENV_DEFAULT.value,
            },
        )
    )
    typer.echo(
        f"Config file created at {constants.SCOACH_DEFAULT_CONFIG_PATH.value}.")

    typer.echo("Setting up database...")
    setup_database()


@app.command()
@logger.catch
def start():
    """
    Run daemon process for SLURM login machine.
    """
    if not check_config():
        return

    typer.echo("Starting scoach daemon process...")
    scoach = Scoach()
    scoach.start_scheduler()
