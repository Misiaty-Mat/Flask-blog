from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Length, Email
from flask_ckeditor import CKEditorField

# Create post WTForm
class CreatePost(FlaskForm):
    title = StringField(
        label="Blog Title",
        validators=[DataRequired(), Length(max=50)]
    )
    
    subtitle = StringField(
        label="Post Subtitle",
        validators=[DataRequired(), Length(max=100)]
    )
    
    image = StringField(
        label="Blog Image URL",
        validators=[DataRequired(), URL()]
    )
    
    content = CKEditorField(
        label="Blog Content",
        validators=[DataRequired()]
    )
    
    submit = SubmitField(
        label="Submit Post",
        render_kw={"style": "margin: 1rem 0; float: right;"}
    )
    
    
class RegisterForm(FlaskForm):
    email = StringField(
        label = "Email",
        validators=[DataRequired(), Email(), Length(max=100)],
    )
    
    password = PasswordField(
        label= "Password",
        validators=[DataRequired(), Length(min=6)]
    )
    
    name = StringField(
        label="Name",
        validators=[DataRequired()]
    )
    
    submit = SubmitField(
        label="Sign me up!",
        render_kw={"style": "margin: 1rem 0;"}
    )
    
    
class LoginForm(FlaskForm):
    email = StringField(
        label = "Email",
        validators=[DataRequired(), Email(), Length(max=100)]
    )
    
    password = PasswordField(
        label= "Password",
        validators=[DataRequired(), Length(min=6)]
    )
    
    submit = SubmitField(
        label="Login",
        render_kw={"style": "margin: 1rem 0;"}
    )
    
class CommentForm(FlaskForm):
    comment = CKEditorField(
        label="Your comment",
        validators=[DataRequired(), Length(max=400)]
    )
    
    submit = SubmitField(
        label="Submit comment",
        render_kw={"style": "margin: 1rem 0;"}
    )

        