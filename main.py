from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:growth@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '73seventythree'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(120))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs =  db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

    @app.before_request
    def require_login():
        allowed_routes = ['login', 'blog', 'index', 'signup']
        if request.endpoint not in allowed_routes and 'username' not in session:    
            return redirect('/login')

@app.route('/', methods=['POST', 'GET'])
def index():
    
    return render_template('index.html',title="Blogz", users=User.query.all())


@app.route('/login', methods=['POST', 'GET'])
def login():

    username = ''
    username_error = ''
    password_error = ''

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if not user:
            username_error = 'Username does not Exist'
        else:   
            password_error = 'Password is Incorrect'
                        
    return render_template('login.html', title='Blogz', username=username, username_error=username_error, password_error=password_error)



@app.route('/signup', methods=['POST', 'GET'])
def signup():

    username = ''
    username_error = ''
    password_error = ''
    verify_error = ''
    multifield_error = ''

   
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
              
        if len(password) < 3:
            password_error = 'Invalid Password!'
        if len(username) < 3:
            username_error = 'Invalid Username!'
        if verify != password:
            verify_error = 'Passwords do not Match!'
        if len(username) == 0 or len(password) == 0 or len(verify) == 0:
            multifield_error = 'One or more fields are Invalid!'
        if len(multifield_error) == 0 and len(username_error) == 0 and len(password_error) == 0 and len(verify_error) == 0:        
            if not existing_user:
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                username_error = 'Username already Exists!'
        
    return render_template('signup.html', username=username, username_error=username_error, password_error=password_error, verify_error=verify_error, multifield_error=multifield_error)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')


@app.route('/blog', methods=[ 'GET'])
def blog():
    # variable for requesting id from database
    blog_id = request.args.get('id')
     # If request is true grab blog using id and render template that returns single blog post
    if blog_id:
        blogs = Blog.query.get(blog_id)
        return render_template('single_blog.html', blogs=blogs)

    user_username = request.args.get('user')
    if user_username:
        users = Blog.query.filter_by(owner_id=user_username)
        return  render_template('single_user.html', users=users)       

    # Render page that holds all blogs
    return render_template('blog.html',title="Blogz", blogs=Blog.query.all(), users=User.query.all())

# this method response to either a post request or get request from 127.0.0.1:5000/newpost
@app.route('/newpost', methods=['Post', 'GET'])
def newpost():

    owner = User.query.filter_by(username=session['username']).first()

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
            new_blog = Blog(blog_title, blog_body, owner)
            # Insert Blog into database
            db.session.add(new_blog)
            # Save database so new blog persists and shows up
            db.session.commit()   
            # Redirect to individual blog post using current blog's information, id is automatically generated once we commit session
            return redirect('blog?id={0}'.format(new_blog.id))

    # If request is a get request, render page that holds a newpost form with all variables being set to empty strings("")
    return render_template('newpost.html',title="Blogz", blogtitle_error=blogtitle_error, blogbody_error=blogbody_error, blog_title=blog_title, blog_body=blog_body) 

if __name__ == '__main__':
    app.run()
    