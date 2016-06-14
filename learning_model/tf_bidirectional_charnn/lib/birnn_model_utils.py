from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import numpy as np
from tensorflow.python.platform import gfile

from tf_bidirectional_charnn.configs.config import FLAGS
from tf_bidirectional_charnn.lib import data_utils
from tf_bidirectional_charnn.lib import birnn_model


def create_model(session, forward_only):
  """Create translation model and initialize or load parameters in session."""

  #hidden_size, max_gradient_norm, vocab_size,label_size,batch_size, num_steps,learning_rate,learning_rate_decay_factor,forward_only=False):
  model = birnn_model.BiRNNClassificationModel(
      hidden_size=FLAGS.hidden_size,
      max_gradient_norm=FLAGS.max_gradient_norm,
      vocab_size=128,
      label_size=7,
      batch_size=FLAGS.batch_size,
      num_steps=FLAGS.num_steps,
      learning_rate=FLAGS.learning_rate,
      learning_rate_decay_factor=FLAGS.learning_rate_decay_factor,
      forward_only=forward_only)
  ckpt = tf.train.get_checkpoint_state(FLAGS.model_dir)
  if ckpt and gfile.Exists(ckpt.model_checkpoint_path):
    print("Reading model parameters from %s" % ckpt.model_checkpoint_path)
    model.saver.restore(session, ckpt.model_checkpoint_path)
  else:
    print("Created model with fresh parameters.")
    session.run(tf.initialize_all_variables())
  return model
