from t2i.visualizer import *
from t2i.highlightBoxNLP import *
from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
from flask import make_response
from flask import jsonify
from flask import send_file
import sys

app = Flask("text2illustrate")
CORS(app, resources=r'/api/*')

# this should return data on highlighted spans.
@app.route('/')
def checkRunning():
    return "Running!"

@app.route('/api/highlight_input', methods=["POST"])
def highlight_input():
    print("Called!", file=sys.stderr)
    error = None
    highlightBoxHandler = HighlightBoxRequestHandler()
    text = request.form['input']
    print(text, file=sys.stderr)
    highlights = highlightBoxHandler.handle(text)
    return jsonify(highlights)

# this should return a large json consisting of filename + eager-executed trajectory.
@app.route('/api/process_text', methods=["POST"])
def process_text():
    print("Called!", file=sys.stderr)
    error = None
    visualizer = Visualizer()
    text = request.form['input']
    print(text, file=sys.stderr)

    titlesAndMotion = visualizer.ServeFileTitleAndMotion(text)
    return jsonify(titlesAndMotion)

