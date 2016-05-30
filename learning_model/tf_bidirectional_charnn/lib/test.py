import os
import sys
import socket
import re
# network functions go here

import tensorflow as tf
from time import sleep
import collections

from tf_seq2seq_chatbot.configs.config import FLAGS
from tf_seq2seq_chatbot.lib import data_utils
from tf_seq2seq_chatbot.lib.seq2seq_model_utils import create_model, _get_predicted_sentence
from tf_seq2seq_chatbot.lib.twitchbot import *
from tf_seq2seq_chatbot.lib import cfg

def chat():
  with tf.Session() as sess:
    # Create model and load parameters.
    model = create_model(sess, forward_only=True)
    model.batch_size = 1  # We decode one sentence at a time.

    # Load vocabularies.
    vocab_path = os.path.join(FLAGS.data_dir, "vocab%d.in" % FLAGS.vocab_size)
    vocab, rev_vocab = data_utils.initialize_vocabulary(vocab_path)

    # Decode from standard input.
    # sys.stdout.write("> ")
    sys.stdout.flush()
    # sentence = sys.stdin.readline()
    past = collections.deque(maxlen=3)
    # past.extendleft([sentence])
    s = socket.socket()
    s.connect((cfg.HOST, cfg.PORT))
    s.send("PASS {}\r\n".format(cfg.PASS).encode("utf-8"))
    s.send("NICK {}\r\n".format(cfg.NICK).encode("utf-8"))
    s.send("JOIN {}\r\n".format(cfg.CHAN).encode("utf-8"))
    s.setblocking(0)
    while True:
        try:
            response = s.recv(1024).decode("utf-8")
            if response == "PING :tmi.twitch.tv\r\n":
                s.send("PONG :tmi.twitch.tv\r\n".encode("utf-8",'ignore'))
            else:
                text = re.findall('PRIVMSG.+?(?=\:)\:(.+?(?=\r))',response)
                for msg in text:
                    past.extendleft([msg.encode('utf-8')])
                # print past
        except:
            pass
        new=[]
        for t in past:
            new.append(t.decode("utf-8",'ignore'))
            # new.append( t.encode('ascii','ignore') )
        sentence= u' '.join(new)
        # print sentence
        predicted_sentence = _get_predicted_sentence(sentence.encode('utf-8','replace'), vocab, rev_vocab, model, sess)
        # predicted_sentence ='Kappa'
        print(predicted_sentence)
        # send_chat(s,predicted_sentence)
        sys.stdout.flush()
        past.extendleft([predicted_sentence])
        # print sentence
        sleep(2)
