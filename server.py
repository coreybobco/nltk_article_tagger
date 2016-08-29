#!/usr/bin/env python2.7

from flask import Flask, request, render_template
from tagger import Tagger_Class as Tagger
import json

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route("/tag", methods=['POST'])
def tag():
    data= json.loads(request.get_data().decode(encoding='UTF-8'))
    tagger = Tagger()
    tagger.tag(data['article'], data['title'])
    if len(tagger.title_tags):
        response = "Title-derived tags:\n\n"
        for tag in tagger.title_tags:
            response += tag + "\n"
    else:
        response = "No title-derived tags."
    response += "\n"
    if len(tagger.title_tags):
        response += "Content-derived tags:\n\n"
        for tag in tagger.body_tags:
            response += tag + "\n"
    else:
        response += "No content-derived tags."
    return response

if __name__ == '__main__':
    app.run(
        host="0.0.0.0",
        port=8080,
        debug=True
    )
