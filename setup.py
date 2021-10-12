from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()


def get_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name="tf_coach",
    version="0.0.1",
    license="GPL-3.0",
    description="Setup for training Tensorflow models on SLURM clusters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    author="Gabriel Gazola Milan",
    author_email="gabriel.gazola@poli.ufrj.br",
    url="https://github.com/gabriel-milan/coach",
    install_requires=get_requirements(),
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
