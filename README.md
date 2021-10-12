# scoach

A setup for training Tensorflow models on SLURM clusters

## How does it work?

- Inputs needed (see examples directory):
  - A `.json` file with parameters for training
  - A `.json` file with the model definition
  - A `.py` file with the training code.
  - There's a CLI app for interacting with scoach
  - Run `scoach init` for setting up your configuration file, such as in `config_example.yaml`
  - On the login machine at the SLURM cluster, run `scoach start`. This will start a daemon that will then launch jobs as requested.
  - On any machine, you can do `scoach run submit` to submit jobs.
  - This will upload the Python script to MinIO and submit the configurations to the database.
  - The new runs are consumed by the daemon process, which then uses Jinja2 to render the training script and submit it to the cluster.
  - The training script is then run on the cluster, using Dask workers, that will grow as needed.

## To do

- [ ] Add support for uploading/managing datasets
- [ ] No Python script duplicates
