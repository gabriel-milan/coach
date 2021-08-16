import tensorflow as tf
from coach.db import save_run

model = tf.keras.models.from_json({{model_config}})

# Do some training

save_run({{run_config}}, model, {{random_seed}}, {{random_seed}}, ["test"])
