from views import views_bp
from apis import api_bp
from flask import Flask

app = Flask(__name__, template_folder="templates")
app.url_map.strict_slashes = False

app.register_blueprint(views_bp)
app.register_blueprint(api_bp)

app.secret_key = "MadhusudhanReddy"


if __name__ == '__main__':
    app.run(debug=True)