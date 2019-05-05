export FLASK_APP=flaskServer.py
flask run -p 3000 &
cd stanford-corenlp-full-2018-10-05
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000 &
cd ..
python3 -m http.server 8000 &

