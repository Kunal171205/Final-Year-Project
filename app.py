from flask import Flask, render_template, jsonify, request, Response, redirect,session,url_for
from pymongo import MongoClient
import os

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods = ["GET","POST"])
def signup():

    if request.method == "POST":
        username = request.form.get("Username")
        email = request.form.get("Email")
        password =  request.form.get("Password")
        phone =  request.form.get("phone")

        session["user"] = username
        
        return redirect(url_for("index"))
    
    return render_template("signup.html")


@app.route("/loginpage", methods=["GET", "POST"])
def Login():

    if request.method == "POST":
        username = request.form.get("Username")
        password =  request.form.get("Password")

        if username == "admin" and password =="123":
            session["user"] = username
            return  redirect(url_for("index"))
        else:
            return Response("invalid")

    return render_template("login.html")



@app.route("/logintype",methods= ["GET","POST"])
def logintype():

    return render_template("LoginHomePage.html")


@app.route("/apply", methods = ["GET","POST"])
def applyjob():
    return render_template("apply-job.html")
    

@app.route("/homeb2b", methods = ["GET","POST"])
def b2bhome():
    return render_template("b2b-home.html")

@app.route("/postb2b", methods = ["GET","POST"])
def b2bpost():
    return render_template("b2b-post.html")

@app.route("/buyerlist", methods = ["GET","POST"])
def buyerlist():
    return render_template("buyer-list.html")

@app.route("/companyprofile", methods = ["GET","POST"])
def companyprofile():
    # Fix template name typo to match actual file: company-profile.html
    return render_template("company-profile.html")

@app.route("/jobportal", methods = ["GET","POST"])
def jobportal():
    return render_template("job-portal.html")

@app.route("/jobpost", methods = ["GET","POST"])
def jobpost():
    return render_template("post-job.html")

@app.route("/hostseller", methods = ["GET","POST"])
def hostseller():
    return render_template("seller-host.html")

@app.route("/application", methods = ["GET","POST"])
def application():
    # Fix template name to match actual file: view-applications.html
    return render_template("view-applications.html")

@app.route("/workerprofile", methods = ["GET","POST"])
def workerprofile():
    return render_template("worker-profile.html")

if __name__ == "__main__":
    app.run(debug=True)