from flask import Flask, render_template, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
import re

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

class JobPOST(db.Model):
    __tablename__ = 'job_post'
    job_id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String(80), nullable=False)
    job_category = db.Column(db.String(128), nullable=False)
    job_location = db.Column(db.String(128), nullable=False)
    job_experience = db.Column(db.String(128), nullable=False)
    job_shift = db.Column(db.String(128), nullable=False)
    job_salary = db.Column(db.String(128), nullable=False)
    job_contact = db.Column(db.String(128), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.String(80), nullable=False)  # Store business username/email

    def __repr__(self):
        return f"<JobPOST {self.job_title} at {self.job_location}>"


class Application(db.Model):
    application_id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job_post.job_id'), nullable=False)
    applicant_name = db.Column(db.String(80), nullable=False)
    applicant_email = db.Column(db.String(120), nullable=False)
    applicant_phone = db.Column(db.String(20), nullable=False)
    applicant_age = db.Column(db.Integer, nullable=False)
    applicant_gender = db.Column(db.String(20), nullable=False)
    applicant_skill = db.Column(db.String(120), nullable=False)
    applicant_experience = db.Column(db.String(120), nullable=False)
    applicant_expected_salary = db.Column(db.String(120), nullable=False)
    applicant_status = db.Column(db.String(20), nullable=False, default="pending")
    application_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    applicant_username = db.Column(db.String(80), nullable=False)  # Link to user who applied

    # Relationship to JobPOST
    job = db.relationship('JobPOST', backref='applications')

    def __repr__(self):
        return f"<Application {self.applicant_name} for Job {self.job_id}>"

class sellitem(db.Model):
    __tablename__ = 'sell_item'
    sell_id = db.Column(db.Integer, primary_key=True)
    sell_name = db.Column(db.String(80), nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    sell_quantity = db.Column(db.Integer, nullable=False)
    sell_description = db.Column(db.Text, nullable=False)
    sell_image = db.Column(db.String(200), nullable=True)  # Made optional for now
    sell_status = db.Column(db.String(20), nullable=False, default="available")
    sell_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posted_by = db.Column(db.String(80), nullable=False)  # Store business username/email
    sell_category = db.Column(db.String(80), nullable=True)  # Category field
    sell_location = db.Column(db.String(128), nullable=True)  # Location field

    def __repr__(self):
        return f"<sellitem {self.sell_name} - ₹{self.sell_price}>"


class buyitem(db.Model):
    __tablename__ = 'buy_item'
    buy_id = db.Column(db.Integer, primary_key=True)
    buy_name = db.Column(db.String(80), nullable=False)
    buy_budget = db.Column(db.Float, nullable=True)  # Optional budget
    buy_quantity = db.Column(db.Integer, nullable=False)
    buy_description = db.Column(db.Text, nullable=False)
    buy_image = db.Column(db.String(200), nullable=True)  # Optional image URL
    buy_status = db.Column(db.String(20), nullable=False, default="open")
    buy_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    posted_by = db.Column(db.String(80), nullable=False)  # Store business username/email
    buy_category = db.Column(db.String(80), nullable=True)  # Category field
    buy_location = db.Column(db.String(128), nullable=True)  # Location field

    def __repr__(self):
        return f"<buyitem {self.buy_name} - Budget: ₹{self.buy_budget if self.buy_budget else 'Negotiable'}>"

    
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

    # Get all applications by this user
    username = session.get("user")
    user_applications = Application.query.filter_by(
        applicant_username=username
    ).order_by(Application.application_date.desc()).all()

    # Get job details for each application
    applications_with_jobs = []
    for app in user_applications:
        job = JobPOST.query.get(app.job_id)
        applications_with_jobs.append({
            'application': app,
            'job': job
        })

    return render_template("worker-profile.html", 
                         applications=applications_with_jobs,
                         username=username)


@app.route("/jobportal")
def jobportal():
    role = session.get("role")

    # If not logged in at all, send to login type selector page
    if role is None:
        return redirect(url_for("logintype"))

    # Only normal users can see the job portal
    if role != "user":
        return redirect(url_for("dashboard"))

    # Fetch all jobs from database
    jobs = JobPOST.query.all()
    return render_template("job-portal.html", jobs=jobs)


@app.route("/apply", methods=["GET", "POST"])
def applyjob():
    if session.get("role") != "user":
        return redirect(url_for("dashboard"))

    # Get job_id from query parameter
    job_id = request.args.get("job_id")
    
    if request.method == "POST":
        # Get form data
        job_id = request.form.get("job_id")
        applicant_name = request.form.get("applicant_name")
        applicant_email = request.form.get("applicant_email")
        applicant_phone = request.form.get("applicant_phone")
        applicant_age = request.form.get("applicant_age")
        applicant_gender = request.form.get("applicant_gender")
        applicant_skill = request.form.get("applicant_skill")
        applicant_experience = request.form.get("applicant_experience")
        applicant_expected_salary = request.form.get("applicant_expected_salary")

        # Validate required fields
        if not all([job_id, applicant_name, applicant_email, applicant_phone, 
                   applicant_age, applicant_gender, applicant_skill, 
                   applicant_experience, applicant_expected_salary]):
            return "All fields are required", 400

        # Check if job exists
        job = JobPOST.query.get(job_id)
        if not job:
            return "Job not found", 404

        # Check if user already applied for this job
        existing_application = Application.query.filter_by(
            job_id=job_id,
            applicant_username=session.get("user")
        ).first()
        
        if existing_application:
            return "You have already applied for this job", 400

        # Create new application
        application = Application(
            job_id=int(job_id),
            applicant_name=applicant_name,
            applicant_email=applicant_email,
            applicant_phone=applicant_phone,
            applicant_age=int(applicant_age),
            applicant_gender=applicant_gender,
            applicant_skill=applicant_skill,
            applicant_experience=applicant_experience,
            applicant_expected_salary=applicant_expected_salary,
            applicant_username=session.get("user")
        )

        db.session.add(application)
        db.session.commit()

        # Redirect to worker profile with success
        return redirect(url_for("workerprofile"))

    # GET request - show application form
    if not job_id:
        return redirect(url_for("jobportal"))

    # Get job details
    job = JobPOST.query.get(job_id)
    if not job:
        return "Job not found", 404

    return render_template("apply-job.html", job=job)


# ===================== BUSINESS ROUTES =====================
@app.route("/companyprofile")
def companyprofile():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    return render_template("company-profile.html")


@app.route("/jobpost", methods=["GET", "POST"])
def jobpost():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Get form data
        job_title = request.form.get("job_title")
        job_category = request.form.get("job_category")
        job_location = request.form.get("job_location")
        job_experience = request.form.get("job_experience")
        job_shift = request.form.get("job_shift")
        job_salary = request.form.get("job_salary")
        job_contact = request.form.get("job_contact")
        job_description = request.form.get("job_description")

        # Validate required fields
        if not all([job_title, job_category, job_location, job_experience, 
                   job_shift, job_salary, job_contact, job_description]):
            return "All fields are required", 400

        # Create new job post
        job = JobPOST(
            job_title=job_title,
            job_category=job_category,
            job_location=job_location,
            job_experience=job_experience,
            job_shift=job_shift,
            job_salary=job_salary,
            job_contact=job_contact,
            job_description=job_description,
            posted_by=session.get("user", "unknown")
        )

        db.session.add(job)
        db.session.commit()

        # Redirect to company profile with success message
        return redirect(url_for("companyprofile"))

    return render_template("post-job.html")


@app.route("/application")
def application():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    # Get job_id from query parameter (optional - to filter by job)
    job_id = request.args.get("job_id")
    business_username = session.get("user")

    # Get all jobs posted by this business
    business_jobs = JobPOST.query.filter_by(posted_by=business_username).all()
    
    if job_id:
        # Show applications for a specific job
        job = JobPOST.query.get(job_id)
        if not job or job.posted_by != business_username:
            return "Job not found", 404
        
        applications = Application.query.filter_by(job_id=job_id).order_by(
            Application.application_date.desc()
        ).all()
        
        # Ensure job relationship is loaded
        for app in applications:
            if not app.job:
                app.job = JobPOST.query.get(app.job_id)
        
        return render_template("view-applications.html", 
                             applications=applications, 
                             job=job,
                             all_jobs=business_jobs)
    else:
        # Show all applications for all jobs posted by this business
        if business_jobs:
            job_ids = [job.job_id for job in business_jobs]
            applications = Application.query.filter(
                Application.job_id.in_(job_ids)
            ).order_by(Application.application_date.desc()).all()
            
            # Ensure job relationships are loaded
            for app in applications:
                if not app.job:
                    app.job = JobPOST.query.get(app.job_id)
        else:
            applications = []
        
        return render_template("view-applications.html", 
                             applications=applications, 
                             job=None,
                             all_jobs=business_jobs)


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


@app.route("/b2bsell", methods=["GET", "POST"])
def b2bpost():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Get form data
        sell_name = request.form.get("sell_name")
        sell_category = request.form.get("sell_category")
        sell_quantity = request.form.get("sell_quantity")
        sell_location = request.form.get("sell_location")
        sell_price = request.form.get("sell_price")
        sell_description = request.form.get("sell_description")
        sell_image = request.form.get("sell_image", "")  # Optional image URL

        # Validate required fields
        if not all([sell_name, sell_quantity, sell_price, sell_description]):
            return "Name, quantity, price, and description are required", 400

        try:
            # Convert price - handle various formats (₹45,000, 45000, 45/kg, etc.)
            price_str = sell_price.replace('₹', '').replace(',', '').replace(' ', '').strip()
            # Extract just the number part (handle cases like "45/kg" or "45000")
            price_match = re.search(r'[\d.]+', price_str)
            if price_match:
                price_float = float(price_match.group())
            else:
                return "Invalid price format. Please enter a number.", 400
            
            # Convert quantity - extract number from string
            quantity_match = re.search(r'\d+', sell_quantity)
            if quantity_match:
                quantity_int = int(quantity_match.group())
            else:
                return "Invalid quantity format. Please enter a number.", 400
        except (ValueError, AttributeError):
            return "Invalid price or quantity format", 400

        # Create new sell item
        sell_item = sellitem(
            sell_name=sell_name,
            sell_category=sell_category or "General",
            sell_quantity=quantity_int,
            sell_location=sell_location or "Not specified",
            sell_price=price_float,
            sell_description=sell_description,
            sell_image=sell_image,
            posted_by=session.get("user", "unknown")
        )

        db.session.add(sell_item)
        db.session.commit()

        # Redirect to B2B home with success
        return redirect(url_for("b2bhome"))

    return render_template("b2b-post.html")


@app.route("/b2bbuy")
def buyerlist():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    # Fetch all available sell items
    sell_items = sellitem.query.filter_by(sell_status="available").order_by(
        sellitem.sell_date.desc()
    ).all()

    # Fetch all open buy requirements
    buy_items = buyitem.query.filter_by(buy_status="open").order_by(
        buyitem.buy_date.desc()
    ).all()

    return render_template("buyer-list.html", sell_items=sell_items, buy_items=buy_items)


@app.route("/hostseller", methods=["GET", "POST"])
def hostseller():
    if session.get("role") != "business":
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        # Get form data for buy requirement
        buy_name = request.form.get("buy_name")
        buy_category = request.form.get("buy_category")
        buy_quantity = request.form.get("buy_quantity")
        buy_location = request.form.get("buy_location")
        buy_budget = request.form.get("buy_budget", "")
        buy_description = request.form.get("buy_description")
        buy_image = request.form.get("buy_image", "")  # Optional image URL

        # Validate required fields
        if not all([buy_name, buy_quantity, buy_description]):
            return "Name, quantity, and description are required", 400

        try:
            # Convert quantity - extract number from string
            quantity_match = re.search(r'\d+', buy_quantity)
            if quantity_match:
                quantity_int = int(quantity_match.group())
            else:
                return "Invalid quantity format. Please enter a number.", 400

            # Convert budget if provided
            budget_float = None
            if buy_budget and buy_budget.strip().lower() not in ['negotiable', 'na', '']:
                budget_str = buy_budget.replace('₹', '').replace(',', '').replace(' ', '').strip()
                budget_match = re.search(r'[\d.]+', budget_str)
                if budget_match:
                    budget_float = float(budget_match.group())

        except (ValueError, AttributeError):
            return "Invalid quantity or budget format", 400

        # Create new buy item
        buy_item = buyitem(
            buy_name=buy_name,
            buy_category=buy_category or "General",
            buy_quantity=quantity_int,
            buy_location=buy_location or "Not specified",
            buy_budget=budget_float,
            buy_description=buy_description,
            buy_image=buy_image,
            posted_by=session.get("user", "unknown")
        )

        db.session.add(buy_item)
        db.session.commit()

        # Redirect to B2B home with success
        return redirect(url_for("b2bhome"))

    return render_template("seller-host.html")


# ===================== LOGOUT =====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ===================== DATABASE INITIALIZATION =====================
# Create all database tables if they don't exist
with app.app_context():
    db.create_all()
    print("✅ Database tables created/verified successfully!")


# ===================== RUN =====================
if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
