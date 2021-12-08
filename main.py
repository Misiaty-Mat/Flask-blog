from functools import wraps
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from flask_ckeditor import CKEditor
from flask_gravatar import Gravatar
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from datetime import datetime
import smtplib
import os

# Local filel
from forms import CreatePost, RegisterForm, LoginForm, CommentForm

#loading enviroment
load_dotenv()

EMAIL_SENDER = os.environ.get("EMAIL_SENDER")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")


# Getting ids od users with admin premmisions
authorizated_users = []
with open("admin_ids.txt") as f:
    for line in f:
        authorizated_users.append(int(line.strip()))

# Get current year
year = datetime.now().year


#flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = "random gibblerish"
Bootstrap(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

ckeditor = CKEditor(app)

gravatar = Gravatar(
    app,
    size=50,
    rating='g',
    default='retro',
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None
    )

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


##CONFIGURE USER TABLE IN DATABASE
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")


##CONFIGURE POST TABLE IN DATABASE
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    
    author = relationship("User", back_populates="posts")
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    
    child_comments = relationship("Comment", back_populates="parent_post")
    
    
##CONFIGURE COMMENT SECTION IN DATABASE
class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text)
    
    
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comment_author = relationship("User", back_populates="comments")
    
    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="child_comments")
    

# Decorator for securing some routes for admin only
def admin_only(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id not in authorizated_users:
            return abort(403)
        return func(*args, **kwargs)
    return inner


# Home page
@app.route('/')
def home():
    blog_posts = BlogPost.query.all()
    return render_template("index.html", posts=blog_posts, year=year, ath_users=authorizated_users)

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
    
    
# Individual post page
@app.route("/post/<int:post_id>", methods=["POST", "GET"])
def post_article(post_id):
    blog_posts = BlogPost.query.all()
    post = blog_posts[post_id-1]
    
    comment_form = CommentForm()
    
    if comment_form.validate_on_submit():
        new_comment = Comment(
            text = comment_form.comment.data,
            
            comment_author = current_user,
            parent_post = post
        )
        
        db.session.add(new_comment)
        db.session.commit()
        
        
        
        return redirect(url_for("post_article", post_id=post_id))
    
    
    
    return render_template("post.html", post_data=post, year=year, ath_users=authorizated_users, form=comment_form)
    
    
# Create post page with wtforms
# Data is added to a database
@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def new_post():
    add_post_form = CreatePost()
    
    if add_post_form.validate_on_submit():
        current_date = datetime.now().strftime("%B %d, %Y")
        
        new_post = BlogPost(
            title = add_post_form.title.data,
            subtitle = add_post_form.subtitle.data,
            date = current_date,
            body = add_post_form.content.data,
            author = current_user,
            img_url = add_post_form.image.data,
        )
        
        db.session.add(new_post)
        db.session.commit()
        
        return redirect(url_for("home"))
        
    return render_template("make-post.html", form=add_post_form, year=year, title_message="New Post")


# Edit post page
# Changing data of specific post in database
@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
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

# Deleting specific post
@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_data = BlogPost.query.get(post_id)
    db.session.delete(post_data)
    db.session.commit()
    return redirect(url_for("home"))
    

@app.route("/register", methods=["POST", "GET"])
def register():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        email = register_form.email.data
        password = generate_password_hash(register_form.password.data, method="pbkdf2:sha256", salt_length=8)
        name = register_form.name.data
        
        if User.query.filter_by(email=email).first():
            flash("Email is already signed to the account.")
            return redirect(url_for("login"))
        else:
            new_user = User(
                email = email,
                password = password,
                name = name
            )
            db.session.add(new_user)
            db.session.commit()
            
            login_user(new_user)
            
            return redirect(url_for("home"))
    
    return render_template("register.html", form=register_form)


@app.route("/login", methods=["POST", "GET"])
def login():
    login_form = LoginForm()
    
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=request.form["email"]).first()
        if user:
            hashed_password = user.password
            login_pasword = login_form.password.data
            if check_password_hash(hashed_password, login_pasword):
                login_user(user)
                return redirect(url_for("home"))
            else:
                flash('Wrong password or email.')
                return redirect(url_for("login"))
        else:
            flash('Wrong password or email.')
            return redirect(url_for("login"))
    else:
        return render_template("login.html", form=login_form)
    

@app.route("/loginout")
def logout():
    logout_user()
    return redirect(url_for("home"))  


# Running app on start
if __name__ == "__main__":
    app.run(debug=True)
