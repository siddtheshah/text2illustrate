# Environment this was tested on is:
# Ubuntu 18.04
# python 3.6.7
# mysql 14.14

# BEFORE RUNNING THIS FILE:
# 
# log into your local mysql service and enter the following:
# CREATE DATABASE text2illustrate;
# This will create a database that text2illustrate can load data into

# Python dependencies
pip install opencv-python
pip install numpy
pip install nltk
pip install spacy
pip install pillow
pip install mysql-connector-python
pip install scipy
pip install flask
pip install flask-cors

# Stanford corenlp server
snap install docker
docker run -itd -p 9000:9000 --name corenlp graham3333/corenlp-complete

# Extra stuff
python -m nltk.downloader wordnet

