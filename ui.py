import os

import cPickle
from flask import Flask, render_template, jsonify
from flask_restful import reqparse

import argparse

from model import Model
import tensorflow as tf


app = Flask(__name__)

parser = reqparse.RequestParser()
parser.add_argument('q', help='Starting string')
parser.add_argument('n', type=int, help='Sample length')
@app.route('/mytroll')
def mytroll():
    args = parser.parse_args()
    q = args.get('q')
    if q:
        q = q.lower()
    n = args.get('n', 30)
    res = None
    model = app.config['MODEL']
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            res = model.sample(sess, app.config['WORDS'], app.config['VOCAB'], n, q, 1, 2, 4, True)
    return jsonify(result=res)


@app.route('/')
def index():
    return render_template('index.html')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='save',
                       help='model directory to load stored checkpointed models from')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()

    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'words_vocab.pkl'), 'rb') as f:
        words, vocab = cPickle.load(f)
    model = Model(saved_args, True)
    app.config['MODEL'] = model
    app.config['WORDS'] = words
    app.config['VOCAB'] = vocab

    app.run()
