from flask import Flask,render_template,request,redirect,url_for,session

from flask_sqlalchemy import SQLAlchemy


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO']=True

db=SQLAlchemy(app)
# secret key to use sessions
app.secret_key = 'abcd'
# creating blog model for saving data of blogs
class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(120))
    body=db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

# creating user model for saving data of users
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(20))
    password=db.Column(db.String(20))
    blogs=db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password
    # to represent object of user as a string
    def __str__(self):
        return str(self.username)


# to check if a link requires login
@app.before_request
def require_login():
    # routes allowed without login
    allowed_routes = ['login', 'blog','index','signup','static','singlepost','singleuser']
    if request.endpoint not in allowed_routes and 'user' not in session:
        return redirect( url_for('login',title='Login'))

# route to index or home page showing all users        
@app.route('/')
def index():
    # getting all users from database
    users=User.query.all()
    return render_template('index.html',title='Home Page',users=users)

# route to blog page showing all blogs

@app.route('/blog')
def blog(): 
    # getting data of all blogs
    blog_posts=Blog.query.all()

    return render_template('blog.html',posts=blog_posts,title='Blog Page')

# route to post a new blog post 

@app.route('/newpost',methods=['POST','GET'])
def newpost():
    #to check for posting of new blog
    if request.method == 'POST':

        blog_title = request.form['title']
        blog_body=request.form['body']
        owner_id=User.query.filter_by(username=session['user']).first()
        blog_data=Blog(title=blog_title,body=blog_body,owner=owner_id)
        #to send errors if a blog post dont have enough info
        if blog_title == '':
            return render_template('newpost.html',title='Create new post',err='Please enter a title for your Blog post')
        if blog_body == '':
            return render_template('newpost.html',title='Create new post',err='Please enter the body of your post',blog_title=blog_title)

        db.session.add(blog_data)
        db.session.commit()
        post_data=Blog.query.filter_by(title=blog_title).first()
        post_id=post_data.id
        #redirect to that blog page
        return redirect( url_for('singlepost',post_id=post_id))

  
    return render_template('newpost.html',title='Create new post')

#route to go to a single post

@app.route('/blog/<int:post_id>')
def singlepost(post_id):

    # getting data of one blog post
    entry=Blog.query.filter_by(id=post_id).one()

    return render_template('singlepost.html',entry=entry)

# route to go to user individual page with blog posts related to that user

@app.route('/blog/<user_name>')
def singleuser(user_name):
    # getting all blogs of user
    user_blogs=User.query.filter_by(username=user_name).first().blogs
    return render_template('singleuser.html',blogs=user_blogs)
    
# route to go to login page
@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        username=request.form['user']
        password=request.form['pass']
        user = User.query.filter_by(username=username).first()
        # if username and password exist
        if user and user.password == password:
            session['user'] = username
            return render_template('newpost.html',title='Create new post')
        # if user exist but password is not same    
        elif user and user.password != password:
            return render_template( 'login.html',err='Password is incorrect for this user')
        # if theres no user     
        elif not user:
            return render_template('login.html',err='This User doesn\'t exist')
    return render_template('login.html',title='Login')






# route to signup page

@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=='POST':
        username=request.form['user']
        password=request.form['pass']
        re_password=request.form['re-pass']
        user = User.query.filter_by(username=username).first()
        # if user already exist
        if user:
            return render_template('signup.html',err='User already exist!',title='Sign up')
            # if user doesn't exist
        elif not user:
            # if username is empty or less than lenght of 3
            if username == '' or len(username) < 3:
                return render_template('signup.html',err='Username is invalid',title='Sign up')
            # if password is empty or less than lenght of 3    
            elif password == '' or len(password) < 3:
                return render_template('signup.html',err='Password is  invalid',title='Sign up')
            # if password is not equal to verify password    
            elif re_password == '' or  password != re_password :
                return render_template('signup.html',err='Password does not match',title='Sign up')    
            # if user doesnot exist and password is equal to verify password than signup
            elif password == re_password:
                new_user = User(username=username, password=password)
                db.session.add(new_user)
                db.session.commit()
                session['user'] = username
                return redirect ( url_for('newpost'))   
    return render_template('signup.html',title='Sign up')

# route to logout

@app.route('/logout')
def logout():
    # deletes user from session
    del session['user']
    return redirect( url_for('blog'))

             
            
        

    return render_template('signup.html',title='Signup')


if __name__=='__main__':
    app.run(debug=True)