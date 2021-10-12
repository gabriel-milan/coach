from sys import exit

import minio
import typer
import psycopg2

from scoach.constants import constants
from scoach.utils import load_config_file_to_envs


def check_config():
    """
    Check if the config file exists.
    """
    if not constants.SCOACH_DEFAULT_CONFIG_PATH.value.exists():
        typer.echo(
            "No config file found. Please run `scoach init` to create one.")
        exit(1)

    load_config_file_to_envs()
    return True


def check_database_exists(db_host: str, db_port: str, db_user: str, db_password: str, db_name: str):
    """
    Check if the database exists.
    """
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.close()
        return True
    except psycopg2.OperationalError:
        return False


def check_minio_connection(minio_host: str, minio_access_key: str, minio_secret_key: str, minio_bucket: str):
    """
    Check if the minio connection works.
    """
    try:
        minio_client = minio.Minio(
            minio_host,
            access_key=minio_access_key,
            secret_key=minio_secret_key,
            secure=False,
        )
        _ = minio_client.list_objects(minio_bucket)
        return True
    except Exception as e:
        typer.echo(f"Error: {e}")
        return False
