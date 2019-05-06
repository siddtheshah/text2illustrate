release: pkill java
release: pkill python
release: pkill flask
release: java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
release: bash init_servers.sh
web: heroku-php-apache2

