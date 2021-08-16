from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="tf_coach",
    version="0.1.0",
    license="GPL-3.0",
    description="Setup for training Tensorflow models on SLURM clusters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="Gabriel Gazola Milan",
    author_email="gabriel.gazola@poli.ufrj.br",
    url="https://github.com/gabriel-milan/coach",
    install_requires=[
        "Jinja2==3.0.1",
        "redis==3.5.3",
        "SQLAlchemy==1.3.18",
        "dask_jobqueue==0.7.3",
        "minio==7.1.0",
        "prefect==0.15.3",
        "PyYAML==5.4.1",
        "sqlalchemy_utils==0.37.8",
        "tensorflow==2.6.0",
        "typer==0.3.2",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    scripts=["bin/coach"],
    keywords="tensorflow tensor machine learning hpc slurm",
)
