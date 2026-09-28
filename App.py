# ==========================================
# APP CONFIGURATION & SETUP
# ==========================================

from flask import Flask

# directs flask to the right folder where the html is kept 
app = Flask(__name__, template_folder='templates/HTML') 
app.secret_key = 'your_unique_secret_key_here' # Required to secure user login sessions

# Import and register the blueprints
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.organiser_route import organiser_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(organiser_bp)

if __name__ == '__main__':
    app.run(debug=True)