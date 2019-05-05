from visualizer import *
from highlightBoxNLP import *
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

@app.route('/api/highlight_input')
def highlight_input():
    error = None
    # highlightBoxHandler = HighlightBoxRequestHandler()
    # text = request.form['input']
    # highlights = highlightBoxHandler.handle(text)
    highlights = [(0, 10, "red")]
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
        # titlesAndMotion = [[("images/dog0.png", [(100, 100, 1), (90, 90, 1), (70, 70, 1)]), ("images/dog1.png", [(0, 0, 1), (10, 10, 1), (30, 30, 1)])], [("images/car0.png", [(100, 100, 1), (90, 90, 1), (70, 70, 1)]), ("images/car1.png", [(0, 0, 1), (10, 10, 1), (30, 30, 1)])]]
        # mock_trajectory = []
        # mock_trajectory2 = []
        # for i in range(500):
        #     mock_trajectory.append((i, i, 1))
        #     mock_trajectory2.append((500 - i, 500 - i, 1))
        # titlesAndMotion = [[("images/waiting1.png", mock_trajectory, (200, 200)), ("images/waiting1.png", mock_trajectory2, (200, 200))], [("images/waiting1.png", mock_trajectory, (200, 200)), ("images/waiting1.png", mock_trajectory2, (200, 200))]]
        
    # titlesAndMotion = [("mock", [(0, 0, 1), (0, 100, 1)])]
    return jsonify(titlesAndMotion)

