from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:1234@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key= "power"

db = SQLAlchemy(app)







class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self,name,body,owner):
        self.name = name 
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique= True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self,username,password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup','index','blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')


@app.route('/', methods=['POST', 'GET'])
def index():
    user_list = User.query.all()

    return render_template('index.html',user_list=user_list)


@app.route('/blog', methods=['POST', 'GET'] ) 
def blog():    
    blogpost = Blog.query.all()
    blogid = request.args.get('id')
    user_name = request.args.get('user')

    
    if user_name:
        user = User.query.filter_by(id =user_name).first()
        blogpost= user.blogs
        return render_template('blog.html',blogpost=blogpost)


    if blogid:
        blogpage = Blog.query.filter_by(id=blogid).first()
        return render_template('singleUser.html',title='Blogz', single_blog=blogpage) #blogpage=blogpage)
        
        
    return render_template('blog.html',title="Blogz",blogpost=blogpost) 
    
        

@app.route('/newpost', methods = ['POST','GET'])
def newpost():
    newpost_error = ''
    body_error = ''
    owner = User.query.filter_by(username=session['username']).first()
    
    if request.method == "GET":
        return render_template('newpost.html',title='New blog entry')#,newpost_error=newpost_error, body_error=body_error)    



    if request.method == 'POST':
        blog_name = request.form['title']
        blog_body = request.form['post']
                

        if blog_name == '':
            newpost_error = 'Your new blog needs a title'
    
        elif blog_body=='':
            body_error = 'You need to add some content to your blog post'    

        elif not newpost_error and not body_error: 
          new_post = Blog(blog_name,blog_body,owner)
          db.session.add(new_post)
          db.session.commit()
          #blogid = new_post.id 
          blogid = str(new_post.id)
          return redirect('/blog?id='+ blogid)

    #return redirect('/blog')
    # else:
        return render_template('newpost.html',title='New blog entry')#,newpost_error=newpost_error, body_error=body_error)







@app.route('/login', methods = ['POST','GET'])
def login():
    
    if request.method == "POST":
         username = request.form['username']
         password = request.form['password']

    #else:      
         user = User.query.filter_by(username=username)
        
         if user and user.password == password:
            session['username'] = username
            flash('Welcome!')
            return redirect('/newpost')

         else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


def check(x):
    message =''
    if len(x) >= 3 and len(x) <= 20 and x != "":
        return message
    else:
        message = "must be between 3-20 characters" 
        return message
    


@app.route('/signup',methods = ['GET','POST'])
def signup():
        if request.method == "GET":
            return render_template('signup.html')
        
        user_error = ''
        password_error = ''
        verify_error = ''
        match = ''
   
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']
            verifypassword = request.form['verify']
            exists = User.query.filter_by(username=username).first()

            user_error = check(username)
            password_error = check(password)

            for user in username:
                if user == " ":
                    user_error = flash("No spaces allowed in your Username",'username_error')

            for i in password:
                if i == " ":
                    password_error = flash("No spaces allowed in your password",'password_error')
            if password != verifypassword:
                verify_error = flash('Passwords do not match','verify_error')


            if not user_error and not password_error and not verify_error and not exists:
                new_account = User(username=username, password=password)
                db.session.add(new_account)
                db.session.commit()
                session['username'] = username
                return redirect('/newpost')
            else:
                #return redirect('/signup')
                return render_template('signup.html', username=username,match=match, user_error = user_error, password_error = password_error, verify_error=verify_error)


@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')





if __name__ == '__main__':
    app.run()