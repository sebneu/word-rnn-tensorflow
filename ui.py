import os

import cPickle
from flask import Flask, render_template, jsonify, Blueprint
from flask_restful import reqparse

import argparse
import logging

from model import Model
import tensorflow as tf


app = Flask(__name__)

ui = Blueprint('ui', __name__, template_folder='templates')


parser = reqparse.RequestParser()
parser.add_argument('q', help='Starting string', default=' ')
parser.add_argument('n', type=int, help='Sample length', default=40)
@ui.route('/mytroll')
def mytroll():
    args = parser.parse_args()
    q = args.get('q')
    if q:
        q = q.lower().encode('utf-8')
    n = args.get('n')
    res = None
    model = Model(saved_args, True)
    with tf.Session() as sess:
        ckpt = tf.train.get_checkpoint_state(app.config['SAVE_DIR'])
        if ckpt and ckpt.model_checkpoint_path:
            tf.global_variables_initializer().run()
            saver = tf.train.Saver(tf.global_variables())
            saver.restore(sess, ckpt.model_checkpoint_path)
            res = model.sample(sess, app.config['WORDS'], app.config['VOCAB'], n, q, 1, 2, 4, True)
    return jsonify(result=res)


@ui.route('/')
def index():
    return render_template('index.html')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--save_dir', type=str, default='save',
                       help='model directory to load stored checkpointed models from')
    parser.add_argument('-p','--port', help="Set port of UI (default is 5003)", type=int, dest='port', default=5003)
    parser.add_argument('--prefix', help="Set URL prefix", default='mytroll')
    args = parser.parse_args()
    return args


if __name__ == "__main__":

    logging.basicConfig(level=logging.DEBUG)
    args = parse_args()

    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'words_vocab.pkl'), 'rb') as f:
        words, vocab = cPickle.load(f)

    app.config['WORDS'] = words
    app.config['VOCAB'] = vocab
    app.config['SAVE_DIR'] = args.save_dir

    url_prefix = args.prefix
    logging.info('Starting App on http://localhost:{}/'.format(args.port) + url_prefix + '/')

    app.register_blueprint(ui, url_prefix='/' + url_prefix)
    app.run(port=args.port, host='0.0.0.0')

