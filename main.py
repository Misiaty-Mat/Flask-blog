from flask import Flask, render_template
from dotenv import load_dotenv
import requests

load_dotenv()

app = Flask(__name__)

blog_url = "https://api.npoint.io/c790b4d5cab58020d391"
response = requests.get(blog_url)
blog_posts = response.json()

@app.route('/')
def home():
    return render_template("index.html", posts=blog_posts)

@app.route('/post/<int:post_id>')
def post_article(post_id):
    post = blog_posts[post_id-1]
    return render_template("post.html", post_data=post)

if __name__ == "__main__":
    app.run(debug=True)
