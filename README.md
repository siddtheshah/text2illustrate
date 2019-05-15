# Text2Illustrate

text2illustrate is a program that seeks to take natural language and create a visual story using image composition. It accomplishes this by extracting entities and relationships from the text input.

Watch the demo:
[![Click to watch demo](https://img.youtube.com/vi/3JWEpoO8me0/0.jpg)](https://www.youtube.com/watch?v=3JWEpoO8me0)

### Status

Basic animations added.

### Overview

![alt text][plan]

[plan]: plan.png

### Primary libraries used

- Stanford CoreNLP
- Spacy
- NLTK
- Vignet (from WordsEye)
- OpenCV
- Tkinter
- FabricJS

### Installation

Follow the pre-instructions in install.sh, and then run the script using bash.

### Running Text2Illustrate

Make sure Stanford NLP Server is running on port 9000

Then run: gunicorn flaskServer:app -p 8000
Which will create the python server to serve the text2illustrate html page.

Open frontend.html using a browser, and try it out!

### Good examples:

> The nimble rabbit jumped over the log. The fox turned and chased the chicken instead.

> Jake moved through the stadium. He was looking for food.

> John was a policeman during his younger years.

> There was a diamond at the gate.

> Jerry brought his hammer to the store.

> Bob dropped the wrench onto the floor. It made a loud clang, and Andy yelped in surprise. He then broke the window. Johnny sighed, grabbing the broom and dustpan.


