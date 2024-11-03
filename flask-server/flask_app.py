from flask import Flask
import jinja2
import os


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

app = Flask(__name__)

@app.route("/")
def home():
    template = jinja_env.get_template('index.html')
    return template.render()

if __name__ == "__main__":
    app.run(debug=True)