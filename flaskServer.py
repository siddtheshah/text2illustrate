from visualizer import *
from highlightBoxNLP import *
from flask import Flask
from flask import request
from flask import make_response
from flask import jsonify
from flask import send_file

app = Flask("text2illustrate")

# this should return data on highlighted spans.
@app.route('/')
def checkRunning():
    return "Running!"

@app.route('/highlight_input')
def highlight_input():
    error = None
    # highlightBoxHandler = HighlightBoxRequestHandler()
    # text = request.form['input']
    # highlights = highlightBoxHandler.handle(text)
    highlights = [(0, 10, "red")]
    return jsonify(highlights)

# this should return a large json consisting of filename + eager-executed trajectory.
@app.route('/process_text')
def process_text():
    error = None
    # visualizer = Visualizer()
    # text = request.form['input']
    # titlesAndMotion = visualizer.ServeFileTitleAndMotion(text)
    titlesAndMotion = [("mock", [(0, 0, 1), (0, 100, 1)])]
    return jsonify(titlesAndMotion)

