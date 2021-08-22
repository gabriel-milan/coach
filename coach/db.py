"""
Provides an interface to the database.
"""

import json
from os.path import join
from os import makedirs

from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database

# pylint: disable=ungrouped-imports
from sqlalchemy import Column, Float, Integer, String, create_engine

from coach.constants import constants
from coach.utils import load_env_as_type, join_tags, get_minio_client, save_to_minio

Base = declarative_base()


class Run(Base):
    """
    Database table for storing runs
    """

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String)
    train_config = Column(String)
    model_config = Column(String)
    train_score = Column(Float)
    validation_score = Column(Float)
    weights_path = Column(String)
    tags = Column(String)

    def __repr__(self):
        return "<Run(run_id={}, train_score={}, validation_score={}, tags={})>".format(
            self.run_id, self.train_score, self.validation_score, self.tags
        )

    def __str__(self):
        return self.__repr__()


class DBManager:
    """
    Helper for DB operations
    """

    def __init__(self, db_path=None):
        db_path = db_path or load_env_as_type(constants.DB_CONNECTION_STRING_ENV.value)
        if db_path is None:
            raise ValueError("Environment DB_CONNECTION_STRING is not set")
        self._engine = create_engine(db_path)
        if not database_exists(self._engine.url):
            create_database(self._engine.url)
        Base.metadata.create_all(self._engine)
        self._session_maker = sessionmaker(bind=self._engine)

    @property
    def session(self) -> Session:
        """
        Returns a DB session
        """
        return self._session_maker()

    # pylint: disable=too-many-arguments
    def add_run(
        self,
        run_id,
        train_config,
        model_config,
        train_score,
        validation_score,
        weights_path,
        tags,
    ):
        """
        Adds a run to the database
        """
        run = Run(
            run_id=run_id,
            train_config=train_config,
            model_config=model_config,
            train_score=train_score,
            validation_score=validation_score,
            weights_path=weights_path,
            tags=tags,
        )
        session = self.session
        session.add(run)
        session.commit()


def save_run(
    train_config: dict,
    model,
    train_score: float,
    validation_score: float,
    tags: list = None,
):
    """
    Saves a run to the database
    """
    # Join tags
    tags = tags or []
    tags = join_tags(tags)
    # Extract model_config (dict) from model
    model_config = model.to_json()
    # Generate unique run_id
    run_id = train_config["run_id"]
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
    db_manager = DBManager()
    db_manager.add_run(
        run_id,
        json.dumps(train_config),
        model_config,
        train_score,
        validation_score,
        weights_path,
        tags,
    )


def load_run(run_id: str):
    """
    Loads a Tensorflow model using data from database
    """
    # pylint: disable=no-name-in-module
    # pylint: disable=import-outside-toplevel
    from tensorflow.keras.models import model_from_json

    # Get run from DB
    db_manager = DBManager()
    run = db_manager.session.query(Run).filter(Run.run_id == run_id).first()
    if run is None:
        raise ValueError("Run {} does not exist".format(run_id))
    # Load model from JSON
    model_config = run.model_config
    model = model_from_json(model_config)
    # Load weights from MinIO
    minio_client = get_minio_client()
    tmp_weights_file = join("/tmp/", run.weights_path)
    minio_client.fget_object(
        load_env_as_type(
            constants.MINIO_BUCKET_ENV.value,
            default=constants.MINIO_BUCKET_ENV_DEFAULT.value,
        ),
        run.weights_path,
        tmp_weights_file,
    )
    # Load weights into model
    model.load_weights(tmp_weights_file)
    return model


def list_all_runs():
    """
    Lists all runs in the database
    """
    db_manager = DBManager()
    runs = db_manager.session.query(Run).all()
    return runs


def get_run(run_id: str):
    """
    Gets a run from the database
    """
    db_manager = DBManager()
    run = db_manager.session.query(Run).filter(Run.run_id == run_id).first()
    return run
