from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")

# ===================== DATABASE CONFIG (SQLALCHEMY) =====================
# Default: local SQLite file "site.db" in the project folder.
# To use MySQL/Postgres etc, change this URI, for example:
#   mysql+pymysql://user:password@localhost/mydb
#   postgresql+psycopg2://user:password@localhost/mydb
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "sqlite:///site.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # user / business

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"

# ===================== HOME =====================
@app.route("/")
def home():
    # Always show home page; user can choose where to go next
    return render_template("home.html")


@app.route("/index")
def index():
    # Legacy route used by old template; just reuse home page
    return redirect(url_for("home"))



# ===================== SIGNUP =====================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        # Worker / normal user signup
        username = request.form.get("username") or request.form.get("Username")
        password = request.form.get("password") or request.form.get("Password")

        if not username or not password:
            return "Username and password are required", 400

        # Check if username already exists
        existing = User.query.filter_by(username=username).first()
        if existing:
            return "Username already taken", 400

        user = User(username=username, password=password, role="user")
        db.session.add(user)
        db.session.commit()

        # Log in the new user
        session["user"] = user.username
        session["role"] = user.role
        return redirect(url_for("dashboard"))

    return render_template("signup.html")


@app.route("/businesssignup", methods=["GET", "POST"])
def businesssignup():
    if request.method == "POST":
        # Business signup – we use email as the unique username key
        email = request.form.get("email")
        password = request.form.get("password") or request.form.get("Password")

        if not email or not password:
            return "Email and password are required", 400

        existing = User.query.filter_by(username=email).first()
        if existing:
            return "Company already registered with this email", 400

        user = User(username=email, password=password, role="business")
        db.session.add(user)
        db.session.commit()

        session["user"] = user.username
        session["role"] = user.role
        return redirect(url_for("dashboard"))

    return render_template("signup-business.html")


# ===================== LOGIN =====================
@app.route("/loginpage", methods=["GET", "POST"])
def login():
    # If already logged in, don't show the login form again
    if "user" in session and "role" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username") or request.form.get("Username")
        password = request.form.get("password") or request.form.get("Password")

        # Look up user in the database
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session["user"] = user.username
            session["role"] = user.role
            return redirect(url_for("dashboard"))

        return "Invalid credentials"

    # GET request: coming from /logintype with ?user_type=...
    user_type = request.args.get("user_type", "user")
    return render_template("login.html", user_type=user_type)


@app.route("/logintype")
def logintype():
    return render_template("LoginHomePage.html")


# ===================== DASHBOARD =====================
@app.route("/dashboard")
def dashboard():
    
    if session.get("role") == "user":
        return redirect(url_for("workerprofile"))

    if session.get("role") == "business":
        return redirect(url_for("companyprofile"))

    return redirect(url_for("login"))


# ===================== USER (WORKER) ROUTES =====================
@app.route("/workerprofile")
def workerprofile():
    if session.get("role") != "user":
        return redirect(url_for("dashboard"))

    return render_template("worker-profile.html")


@app.route("/jobportal")
def jobportal():
    role = session.get("role")

    # If not logged in at all, send to login type selector page
    if role is None:
        return redirect(url_for("logintype"))

    # Only normal users can see the job portal
    if role != "user":
        return redirect(url_for("dashboard"))

    return render_template("job-portal.html")


@app.route("/apply")
def applyjob():
    if session.get("role") != "user":
        return redirect(url_for("dashboard"))

    return render_template("apply-job.html")


# ===================== BUSINESS ROUTES =====================
@app.route("/companyprofile")
def companyprofile():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("company-profile.html")


@app.route("/jobpost")
def jobpost():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("post-job.html")


@app.route("/application")
def application():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("view-applications.html")


# ===================== B2B (OPTIONAL BUSINESS PAGES) =====================
@app.route("/homeb2b")
def b2bhome():
    role = session.get("role")

    # If not logged in at all, send to login type selector page
    if role is None:
        return redirect(url_for("logintype"))

    if role != "business":
        return redirect(url_for("dashboard"))

    return render_template("b2b-home.html")


@app.route("/b2bsell")
def b2bpost():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("b2b-post.html")


@app.route("/b2bbuy")
def buyerlist():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("buyer-list.html")


@app.route("/hostseller")
def hostseller():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("seller-host.html")


# ===================== LOGOUT =====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=True)
