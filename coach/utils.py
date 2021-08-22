"""
General utilities
"""

import os
import yaml

from minio import Minio

from coach.constants import constants


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
    # pylint: disable=unspecified-encoding
    # pylint: disable=invalid-name
    with open(constants.COACH_DEFAULT_CONFIG_PATH.value, "r") as f:
        config = yaml.safe_load(f)
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
