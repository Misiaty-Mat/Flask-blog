from flask import Flask, render_template
from dotenv import load_dotenv
from datetime import datetime
import requests

#loading enviroment
load_dotenv()

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
    return render_template('about.html', year=year)

# Contact page
@app.route('/contact')
def contact_page():
    return render_template('contact.html', year=year)

# Running app on start
if __name__ == "__main__":
    app.run(debug=True)
