#!/usr/bin/env python2.7

from flask import Flask, request, render_template
from tagger import Tagger_Class as Tagger

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route("/tag", methods=['POST'])
def tag():
    article = request.get_data().decode(encoding='UTF-8')
    tagger = Tagger()
    tagger.tag(article)
    # wordcount = int(request.args.get('wordcount'))
    # format = request.args.get('format')
    # return markov.generate_output(clean(, format), wordcount, format)


if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )
