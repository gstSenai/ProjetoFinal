from flask import Flask, render_template, url_for, request, redirect

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/post', methods=['GET', 'POST'])
def PostNovo():
    return render_template('post.html')



