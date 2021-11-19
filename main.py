from flask import Flask, render_template, request
from dotenv import load_dotenv
from datetime import datetime
import requests
import smtplib
import os

#loading enviroment
load_dotenv()

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

#flask setup
app = Flask(__name__)

# API conection and JSON file reading
blog_url = "https://api.npoint.io/e798406fdfe498afdabe"
response = requests.get(blog_url)
blog_posts = response.json()

# Get current year
year = datetime.now().year

# Home page
@app.route('/')
def home():
    return render_template("index.html", posts=blog_posts, year=year)

# Individual post page
@app.route('/post/<int:post_id>')
def post_article(post_id):
    post = blog_posts[post_id-1]
    return render_template("post.html", post_data=post, year=year)

# About page
@app.route('/about')
def about_page():
    return render_template("about.html", year=year)

# Contact page
@app.route('/contact', methods=["GET", "POST"])
def contact_page():
    #Getting data from form on contact page
    if request.method == "POST":
        form_name = request.form["name"]
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        message = request.form["message"]
        
        #Message structure
        message_to_send = f"Subject:E-mail from {form_name}\n\nMessage from e-mail: {email}\nPhone number: {phone_number}\n Message:\n{message}"
        
        #Sending e-mail
        with smtplib.SMTP("smtp.gmail.com") as connection:
            connection.starttls()
            connection.login(user=EMAIL_SENDER, password=EMAIL_PASSWORD)
            connection.sendmail(from_addr=EMAIL_SENDER, to_addrs="m.a.s.m@wp.pl", msg=message_to_send)
        return "<h1>Message sended</h1>"
    else:
        #Render page
        return render_template("contact.html", year=year)

# Running app on start
if __name__ == "__main__":
    app.run(debug=True)
