from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


@app.route('/about.html')
def about():
    return render_template('about.html')


@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/blog.html')
def blog():
    return render_template('blog.html')


@app.route('/sidebar-left.html')
def sidebar_left():
    return render_template('sidebar-left.html')


@app.route('/sidebar-right.html')
def sidebar_right():
    return render_template('sidebar-right.html')


@app.route('/single.html')
def single():
    return render_template('single.html')


if __name__ == '__main__':
    app.run()
