# Coach

A setup for training Tensorflow models on SLURM clusters

## How does it work?

- Inputs needed (see examples directory):
  - A `.json` file with parameters for training
  - A `.json` file with the model definition
  - A `.py` file with the training code.
- There's a CLI app for interacting with Coach
- Run `coach init` for setting up your configuration file, such as in `config_example.yaml`
- On the login machine at the SLURM cluster, run `coach daemon`. This will start a daemon that will then launch jobs as requested.
- On any machine, you can do `coach submit` to submit jobs.
  - This will upload the Python script to MinIO and submit the configurations to a Redis queue.
  - The Redis queue is consumed by the daemon, which then uses Jinja2 to render the training script and submit it to the cluster.
  - The training script is then run on the cluster, using Dask workers, that will grow as needed.

## To do

- [ ] Add support for uploading/managing datasets
- [ ] Reusable Python scripts
- [ ] No loading tensorflow at all, except when explicitly needed
- [ ] Replace Redis PubSub with Redis Queue