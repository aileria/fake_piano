import webview
import threading
from multiprocessing import Process
from flask import Flask, render_template
import fake_piano

WINDOW_TITLE = 'FakePiano'

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/play")
def play():
    fake_piano.main()
    return render_template("piano_view.html")

# Start flask
def start_flask():
    app.run()
server = Process(target=start_flask)
server.start()

# Start Program window
window = webview.create_window(WINDOW_TITLE, 'http://127.0.0.1:5000/')
webview.start()
window.toggle_fullscreen()

server.terminate()
server.join()