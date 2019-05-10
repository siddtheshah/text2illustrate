# Environment this was tested on is:
# Ubuntu 18.04
# python 3.6.7
# mysql 14.14
# Docker 18.06.1

# BEFORE RUNNING THIS FILE:
# 
# log into your local mysql service and enter the following:
# CREATE DATABASE text2illustrate;
# This will create a database that text2illustrate can load data into

# Also set the following variable to your mysql username

username=<YOUR USERNAME HERE>

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
docker run -itd -p 9000:9000 --name corenlp graham3333/corenlp-complete

# Create images folder and turn them into transparent PNGs.
unzip images.zip images
./makePNGs.sh

# Extra stuff
python -m nltk.downloader wordnet

# Database loading
mysql -u $username -p text2illustrate < vignet/vignetSizes.sql
mysql -u $username -p text2illustrate < databaseProcessing/imageIndex.sql

# Afterward, you'll have to configure t2i/assetBook.py to use your login credentials for # your sql server. 




