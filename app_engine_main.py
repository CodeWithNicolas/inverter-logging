# This file is required for Google App Engine
# but we're only serving static files, so it's minimal

from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    # This shouldn't be called since we're serving static files
    return "Solar Dashboard"

if __name__ == '__main__':
    app.run(debug=True) 