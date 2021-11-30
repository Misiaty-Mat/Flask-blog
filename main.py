from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditor, CKEditorField
from dotenv import load_dotenv
from datetime import datetime
import requests
import smtplib
import os

#loading enviroment
load_dotenv()

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

# Get current year
year = datetime.now().year


#flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


# Create post form
class CreatePost(FlaskForm):
    title = StringField(
        label="Blog Title",
        validators=[DataRequired(), Length(max=50)])
    
    subtitle = StringField(
        label="Post Subtitle",
        validators=[DataRequired(), Length(max=100)])
    
    name = StringField(
        label="Your Name",
        validators=[DataRequired(), Length(max=50)])
    
    image = StringField(
        label="Blog Image URL",
        validators=[DataRequired(), URL()])
    
    content = CKEditorField(
        label="Blog Content",
        validators=[DataRequired()])
    
    submit = SubmitField(
        label="Submit Post",
        render_kw={"style": "margin: 1rem 0; float: right;"})

        


# Home page
@app.route('/')
def home():
    blog_posts = BlogPost.query.all()
    return render_template("index.html", posts=blog_posts, year=year)


# Create post page with wtforms
# Data is added to a database
@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    add_post_form = CreatePost()
    
    if add_post_form.validate_on_submit():
        current_date = datetime.now().strftime("%B %d, %Y")
        
        new_post = BlogPost(
            title = add_post_form.title.data,
            subtitle = add_post_form.subtitle.data,
            date = current_date,
            body = add_post_form.content.data,
            author = add_post_form.name.data,
            img_url = add_post_form.image.data
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return redirect(url_for("home"))
        
    return render_template("make-post.html", form=add_post_form, year=year, title_message="New Post")


# Edit post page
# Changing data of specific post in database
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
def edit_post(post_id):
    post_data = BlogPost.query.get(post_id)
    
    edit_post_form = CreatePost(
        title=post_data.title,
        subtitle=post_data.subtitle,
        image=post_data.img_url,
        name=post_data.author,
        content=post_data.body
    )
    
    if edit_post_form.validate_on_submit():
        post_data.title = edit_post_form.title.data
        post_data.subtitle = edit_post_form.subtitle.data
        post_data.body = edit_post_form.content.data
        post_data.author = edit_post_form.name.data
        post_data.img_url = edit_post_form.image.data
        
        db.session.commit()
        
        return redirect(url_for("post_article", post_id=post_id))
        
    
    return render_template("make-post.html", form=edit_post_form, year=year, title_message="Edit Post")

# Individual post page
@app.route("/post/<int:post_id>")
def post_article(post_id):
    blog_posts = BlogPost.query.all()
    post = blog_posts[post_id-1]
    return render_template("post.html", post_data=post, year=year)

# Deleting specific post
@app.route("/delete/<int:post_id>")
def delete_post(post_id):
    post_data = BlogPost.query.get(post_id)
    db.session.delete(post_data)
    db.session.commit()
    return redirect(url_for("home"))
    
# About page
@app.route("/about")
def about_page():
    return render_template("about.html", year=year)

# Contact page
@app.route("/contact", methods=["GET", "POST"])
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
