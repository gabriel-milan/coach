import tensorflow as tf
from coach.utils import save_run

from time import sleep

model = tf.keras.models.model_from_json({{model_config}})

# Do some training
sleep(2)

save_run({{run_id}}, model, {{random_seed}}, {{random_seed}})
