from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:built@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))

    def __init__(self, title, body):
        self.title = title
        self.body = body
    

@app.route('/blog', methods=[ 'GET'])
def index():
    # variable for requesting id from database
    blog_id = request.args.get('id')

    # If request is true grab blog using id and render template that returns single blog post
    if blog_id:

        blogs = Blog.query.get(blog_id)
        return render_template('single_blog.html', blogs=blogs)

    # Render page that holds all blogs
    return render_template('blog.html',title="Build A Blog", blogs=Blog.query.all())

# this method response to either a post request or get request from 127.0.0.1:5000/newpost
@app.route('/newpost', methods=['Post', 'GET'])
def newpost():

    # Setting empty variables to store errors if an error exists
    blogtitle_error = ''
    blogbody_error = ''

    # Setting empty variables to be used throughout the scope of def newpost():
    blog_title = ''
    blog_body = ''

    # if request method is post, then validate incoming data, if valid submit post, else re-render page with errors
    if request.method == 'POST':
        # get request keys from post request
        blog_title = request.form['blogtitle']
        blog_body = request.form['blogbody']

        # validation, if blog_title is empty, fill blogtitle_error with a message
        if len(blog_title) == 0:
            blogtitle_error = 'Please fill in the title'

        # validation, if blog_body is empty, fill blogbody_error with a message
        if len(blog_body) == 0:
            blogbody_error = 'Please fill in the body'

        # check messages, if both are empty, then submission is valid, save submissions and redirect to display individual entry
        if len(blogtitle_error) == 0 and len(blogbody_error) == 0:
            # Making a Blog object to be inserted into the database
            new_blog = Blog(blog_title, blog_body)
            # Insert Blog into database
            db.session.add(new_blog)
            # Save database so new blog persists and shows up
            db.session.commit()   
            # Redirect to individual blog post using current blog's information, id is automatically generated once we commit session
            return redirect('blog?id={0}'.format(new_blog.id))

    # If request is a get request, render page that holds a newpost form with all variables being set to empty strings("")
    return render_template('newpost.html',title="Build A Blog", blogtitle_error=blogtitle_error, blogbody_error=blogbody_error, blog_title=blog_title, blog_body=blog_body) 

if __name__ == '__main__':
    app.run()
    