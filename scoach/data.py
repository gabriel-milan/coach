# from os import getenv

# import hub

# from scoach.constants import constants
# from scoach.utils import load_config_file_to_envs

# # TODO: In the future, we could use Hub for data management
# class Dataset (hub.dataset):
#     def __new__(cls, path: str, *args, **kwargs):
#         load_config_file_to_envs()
#         path = f"""s3://{
#             getenv(constants.MINIO_BUCKET_ENV.value)
#         }/{constants.DATASETS_PATH_PREFIX.value}/{path}"""
#         print(path)
#         return super().__new__(
#             cls,
#             path,
#             creds={
#                 "aws_access_key_id": getenv(constants.MINIO_ACCESS_KEY_ENV.value),
#                 "aws_secret_access_key": getenv(constants.MINIO_SECRET_KEY_ENV.value),
#                 "endpoint_url": f"""{getenv(
#                         constants.MINIO_ENDPOINT_SCHEMA_ENV.value
#                     )}://{getenv(
#                         constants.MINIO_ENDPOINT_ENV.value
#                     )}:{getenv(constants.MINIO_ENDPOINT_PORT_ENV.value)}""",
#             },
#             *args,
#             **kwargs
#         )
