"""Sequence-to-sequence model with an attention mechanism."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import random
import numpy as np
from six.moves import xrange  # pylint: disable=redefined-builtin
import tensorflow as tf

# from tensorflow.models.rnn import rnn_cell
# from tensorflow.models.rnn import seq2seq


from tf_seq2seq_chatbot.lib import data_utils


class BiRNNClassificationModel(object):
  """Bidirectional RNN Model mapping from inputs to token by token classification.

  This class implements a single-layer recurrent neural network which classifies
  each input into a range of categories.  This model could be used for NER, part
  of speech tagging, or any similar task.
  """

  def __init__(self, hidden_size, max_gradient_norm, vocab_size,label_size,
               batch_size, num_steps,learning_rate,learning_rate_decay_factor,
               forward_only=False):
    """Create the model.

    Args:
      hidden_size: number of units in each layer of the model.
      max_gradient_norm: gradients will be clipped to maximally this norm.
      batch_size: the size of the batches used during training;
        the model construction is independent of batch_size, so it can be
        changed after initialization if this is convenient, e.g., for decoding.
      learning_rate: learning rate to start with.
      learning_rate_decay_factor: decay learning rate by this much when needed.
      use_lstm: if true, we use LSTM cells instead of GRU cells.
      num_samples: number of samples for sampled softmax.
      forward_only: if set, we do not construct the backward pass in the model.
    """
    self.batch_size = batch_size
    self.learning_rate = tf.Variable(float(learning_rate), trainable=False)
    self.learning_rate_decay_op = self.learning_rate.assign(
        self.learning_rate * learning_rate_decay_factor)
    self.global_step = tf.Variable(0, trainable=False)
    self.num_steps = num_steps
    # logdir='logs/train/'
    self.trainwriter = tf.train.SummaryWriter('logs/train/')
    self.devwriter = tf.train.SummaryWriter('logs/dev/')


    # Create the internal multi-layer cell for our RNN.
    forward_cell = tf.nn.rnn_cell.LSTMCell(hidden_size)
    back_cell = tf.nn.rnn_cell.LSTMCell(hidden_size)

    self.input_placeholder = tf.placeholder(tf.int32,  shape=(self.batch_size,self.num_steps))
    self.labels_placeholder= tf.placeholder(tf.int32,  shape=(self.batch_size,self.num_steps))

    self.istate_fw = tf.placeholder("float", [None, 2*hidden_size])
    self.istate_fw = tf.placeholder("float", [None, 2*hidden_size])


    # Feeds for inputs.
    self.inputs = [tf.unpack(self.input_placeholder,1)]
    self.labels = [tf.unpack(self.labels_placeholder,1)]

    rnn_outputs,forward_out,_ = rnn.bidirectional_rnn(forward_cell, back_cell, input_placeholder,
                                            initial_state_fw=istate_fw,
                                            initial_state_bw=istate_bw)

    def output_projection(rnn_out):
        with tf.variable_scope("projection") as scope:
            U = tf.get_variable("U",(2*self.hidden_size,self.label_size),tf.float32)
            b = tf.get_variable("b",(self.label_size),tf.float32,tf.zeros)
            return tf.matmul(rnn_out,U)+b

    self.projections = []
    for rnn_out in rnn_outputs:
        self.projections.append(output_projection(rnn_out))

    losses = []
    for i in range(len(projections)):
        losses.append(tf.nn.sparse_softmax_cross_entropy_with_logits(projections[i], self.labels[i])

    self.loss = tf.add_n(losses)
    # Training outputs and losses.
    self.loss_summary = tf.scalar_summary("loss", self.loss)
      # If we use output projection, we need to project outputs for decoding.

    # Gradients and SGD update operation for training the model.
    params = tf.trainable_variables()
    if not forward_only:
      self.gradient_norms = []
      self.updates = []
      # TODO: try AdagradOptimizer or RMSPropOptimizer
      opt = tf.train.AdagradOptimizer(self.learning_rate)
      gradients = tf.gradients(self.loss, params, aggregation_method=2)
      clipped_gradients, norm = tf.clip_by_global_norm(gradients,
                                                     max_gradient_norm)
      self.gradient_norm = (norm)
      self.update = opt.apply_gradients(zip(clipped_gradients, params), global_step=self.global_step)
    self.saver = tf.train.Saver(tf.all_variables())

  def step(self, session, encoder_inputs, decoder_inputs, target_weights,
           bucket_id, forward_only,step=0):
    """Run a step of the model feeding the given inputs.

    Args:
      session: tensorflow session to use.
      encoder_inputs: list of numpy int vectors to feed as encoder inputs.
      decoder_inputs: list of numpy int vectors to feed as decoder inputs.
      target_weights: list of numpy float vectors to feed as target weights.
      bucket_id: which bucket of the model to use.
      forward_only: whether to do the backward step or only forward.

    Returns:
      A triple consisting of gradient norm (or None if we did not do backward),
      average perplexity, and the outputs.

    Raises:
      ValueError: if length of enconder_inputs, decoder_inputs, or
        target_weights disagrees with bucket size for the specified bucket_id.
    """
    # Check if the sizes match.

    # Input feed: encoder inputs, decoder inputs, target_weights, as provided.
    input_feed = {}
    input_feed[self.input_placeholder] = inputs
    input_feed[self.labels_placeholder] = labels

    # Output feed: depends on whether we do a backward step or not.
    if not forward_only:
      output_feed = [self.loss_summary,self.update,  # Update Op that does SGD.
                     self.gradient_norm,  # Gradient norm.
                     self.loss]  # Loss for this batch.
    else:
      output_feed = [self.loss_summary,self.loss]  # Loss for this batch.
      for proj in self.projections:
          output_feed.append(proj)

    outputs = session.run(output_feed, input_feed)
    m = outputs[0]
    if not forward_only:
        self.trainwriter.add_summary(m,step)
    else:
        self.devwriter.add_summary(m,step)
    if not forward_only:
      return outputs[2], outputs[3], None  # Gradient norm, loss, no outputs.
    else:
      return None, outputs[1], outputs[2:]  # No gradient norm, loss, outputs.
