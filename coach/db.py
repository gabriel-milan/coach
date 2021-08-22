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


class Scripts(Base):
    """
    Database table for storing scripts path.
    """

    __tablename__ = "scripts"

    id = Column(Integer, primary_key=True)
    script_id = Column(String, unique=True)
    script_path = Column(String)

    def __repr__(self):
        return "<Script(script_id={}, path={})>".format(
            self.script_id, self.script_path
        )

    def __str__(self):
        return self.__repr__()


class Run(Base):
    """
    Database table for storing runs
    """

    __tablename__ = "runs"

    id = Column(Integer, primary_key=True)
    run_id = Column(String, unique=True)
    train_config = Column(String)
    model_config = Column(String)
    train_score = Column(Float)
    validation_score = Column(Float)
    weights_path = Column(String)
    tags = Column(String)
    status = Column(String)

    def __repr__(self):
        return "<Run(run_id={}, status={}, train_score={}, validation_score={}, tags={})>".format(
            self.run_id, self.status, self.train_score, self.validation_score, self.tags
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
        status,
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
            status=status,
        )
        session = self.session
        session.add(run)
        session.commit()

    def get_run(self, run_id):
        """
        Returns a run from the database
        """
        session = self.session
        return session.query(Run).filter(Run.run_id == run_id).first()

    def update_run(self, run: Run):
        """
        Updates a run in the database
        """
        session = self.session
        session.merge(run)
        session.commit()

    def update_run_status(self, run_id, status):
        """
        Updates a run's status in the database
        """
        session = self.session
        run = session.query(Run).filter(Run.run_id == run_id).first()
        run.status = status
        session.commit()

    def create_empty_run(self, run_id):
        """
        Creates an empty run in the database
        """
        session = self.session
        run = Run(run_id=run_id, status=constants.RUN_STATUS_QUEUED.value)
        session.add(run)
        session.commit()

    def delete_run(self, run_id):
        """
        Deletes a run from the database
        """
        session = self.session
        session.query(Run).filter(Run.run_id == run_id).delete()
        session.commit()

    def add_script(self, script_id, script_path):
        """
        Adds a script to the database
        """
        session = self.session
        script = Scripts(script_id=script_id, script_path=script_path)
        session.add(script)
        session.commit()

    def get_script(self, script_id):
        """
        Returns a script from the database
        """
        session = self.session
        return session.query(Scripts).filter(Scripts.script_id == script_id).first()

    def get_script_path(self, script_id):
        """
        Returns a script path from the database
        """
        script = self.get_script(script_id)
        return script.script_path

    def get_all_scripts(self):
        """
        Returns all scripts from the database
        """
        session = self.session
        return session.query(Scripts).all()


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
    run = db_manager.get_run(run_id)
    if run:
        run.train_config = json.dumps(train_config)
        run.model_config = model_config
        run.train_score = train_score
        run.validation_score = validation_score
        run.weights_path = weights_path
        run.tags = tags
        run.status = constants.RUN_STATUS_COMPLETED.value
        db_manager.update_run(run)
    else:
        db_manager.add_run(
            run_id,
            json.dumps(train_config),
            model_config,
            train_score,
            validation_score,
            weights_path,
            tags,
            constants.RUN_STATUS_COMPLETED.value,
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


def delete_run_from_db(run_id: str):
    """
    Deletes a run from the database
    """
    db_manager = DBManager()
    db_manager.session.query(Run).filter(Run.run_id == run_id).delete()
    db_manager.session.commit()
