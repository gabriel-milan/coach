"""
General utilities
"""

import os
from os.path import join
from os import makedirs
from typing import Any
from sys import exit

import yaml
import typer
from minio import Minio
import django
from django.db import models
from django.core import management

from scoach.constants import constants
from scoach.logging import logger


def load_env_as_type(env_name, env_type=str, default=None):
    """
    Loads an environment variable as a certain type.
    """
    env_value = os.environ.get(env_name)
    # pylint: disable=no-else-return
    if env_value is None:
        return default
    elif env_type == int:
        return int(env_value)
    elif env_type == bool:
        return env_value.lower() in ["true", "yes", "1", "y"]
    elif env_type == str:
        return env_value
    else:
        raise ValueError("Unknown type: %s" % env_type)


def get_minio_client(
    minio_access_key: str = None,
    minio_secret_key: str = None,
    minio_url: str = None,
    minio_bucket: str = None,
):
    """
    Get a Minio client for the given Minio URL and bucket.
    """
    minio_access_key = minio_access_key or load_env_as_type(
        constants.MINIO_ACCESS_KEY_ENV.value,
        str,
        constants.MINIO_ACCESS_KEY_ENV_DEFAULT.value,
    )
    minio_secret_key = minio_secret_key or load_env_as_type(
        constants.MINIO_SECRET_KEY_ENV.value,
        str,
        constants.MINIO_SECRET_KEY_ENV_DEFAULT.value,
    )
    minio_url = minio_url or load_env_as_type(
        constants.MINIO_ENDPOINT_ENV.value,
        str,
        constants.MINIO_ENDPOINT_ENV_DEFAULT.value,
    )
    minio_bucket = minio_bucket or load_env_as_type(
        constants.MINIO_BUCKET_ENV.value, str, constants.MINIO_BUCKET_ENV_DEFAULT.value
    )
    if not minio_url:
        raise ValueError("Missing Minio URL")
    if not minio_bucket:
        raise ValueError("Missing Minio bucket")
    return Minio(minio_url, access_key=minio_access_key, secret_key=minio_secret_key)


def join_tags(tags: list) -> str:
    """
    Merge tags into a single string.
    """
    return ",".join(tags)


def split_tags(tags: str) -> list:
    """
    Split tags into a list of tags
    """
    return tags.split(",")


def load_config_file_to_envs():
    """
    Loads the config file to environment variables.
    """
    if not constants.SCOACH_DEFAULT_CONFIG_PATH.value.exists():
        typer.echo(
            "No config file found. Please run `scoach init` to create one.")
        exit(1)
    # pylint: disable=unspecified-encoding
    # pylint: disable=invalid-name
    with open(constants.SCOACH_DEFAULT_CONFIG_PATH.value, "r") as f:
        config: dict = yaml.safe_load(f)
    for key, value in config.items():
        os.environ[key] = str(value)


def save_to_minio(minio_client: Minio, file_path: str, file_name: str):
    """
    Save a file to MinIO
    """
    minio_client.fput_object(
        load_env_as_type(
            constants.MINIO_BUCKET_ENV.value,
            default=constants.MINIO_BUCKET_ENV_DEFAULT.value,
        ),
        file_path,
        file_name,
    )


def download_from_minio(minio_client: Minio, file_path: str, file_name: str):
    """
    Download a file from MinIO
    """
    minio_client.fget_object(
        load_env_as_type(
            constants.MINIO_BUCKET_ENV.value,
            default=constants.MINIO_BUCKET_ENV_DEFAULT.value,
        ),
        file_path,
        file_name,
    )


def safe_object_get(T: models.Model, **kwargs):
    """
    Safely get an object from the database.
    """
    try:
        return T.objects.get(**kwargs)
    except T.DoesNotExist:
        return None


def safe_cast(value: str, to_type: type, default: Any = None):
    """
    Safely cast a value to a given type.
    """
    try:
        return to_type(value)
    except ValueError:
        return default


def save_run(run_id: str, model, train_score: float, validation_score: float):
    """
    Save a run to the database.
    """
    from scoach.models import Run, Weights
    # Cast types
    train_score = safe_cast(train_score, float, None)
    if train_score is None:
        raise ValueError("Train score is not a float")
    validation_score = safe_cast(validation_score, float, None)
    if validation_score is None:
        raise ValueError("Validation score is not a float")
    # Ensure run exists
    run = safe_object_get(Run, id=run_id)
    if run is None:
        raise ValueError(f"Run #{run_id} does not exist")
    # Generate unique weights_path
    weights_path = join(constants.WEIGHTS_PATH_PREFIX.value, f"{run_id}.h5")
    tmp_weights_file = join("/tmp/", weights_path)
    makedirs(tmp_weights_file.rsplit("/", 1)[0], exist_ok=True)
    # Save weights locally
    model.save_weights(tmp_weights_file)
    # Save weights on MinIO
    minio_client = get_minio_client()
    save_to_minio(minio_client, weights_path, tmp_weights_file)
    # Save run on DB
    run: Run = safe_object_get(Run, id=run_id)
    if run:
        run.train_score = train_score
        run.validation_score = validation_score
        weights: Weights = Weights.objects.create(
            path=weights_path,
        )
        weights.save()
        run.weights = weights
        run.save()
    else:
        raise ValueError("Run does not exist")


def load_run(run_id: str):
    """
    Load a run from the database.
    """
    # pylint: disable=no-name-in-module
    # pylint: disable=import-outside-toplevel
    from tensorflow.keras.models import model_from_json
    from scoach.models import Run, Weights

    run: Run = safe_object_get(Run, id=run_id)
    if run:
        weights: Weights = run.weights
        weights_path = weights.path
        # Download weights from MinIO
        minio_client = get_minio_client()
        tmp_weights_file = join("/tmp/", weights_path)
        download_from_minio(minio_client, weights_path,
                            tmp_weights_file)
        # Load weights locally
        model = model_from_json(run.model.config)
        model.load_weights(tmp_weights_file)
        # Remove weights locally
        os.remove(join("/tmp/", weights_path))
        return model
    else:
        raise ValueError("Run not found")


def setup_django():
    load_config_file_to_envs()
    mode = os.getenv(constants.DJANGO_SETTINGS_MODE_ENV.value,
                     constants.DJANGO_SETTINGS_MODE_ENV_DEFAULT.value)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'scoach.settings.{mode}')
    try:
        django.setup()
    except RuntimeError as e:
        if "populate() isn't reentrant" not in str(e):
            raise e


def setup_database():
    setup_django()
    management.execute_from_command_line(
        ['manage.py', 'makemigrations', 'scoach'])
    management.execute_from_command_line(['manage.py', 'migrate'])
