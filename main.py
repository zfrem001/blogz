from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:12345@localhost:3306/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    body = db.Column(db.String(500))

    def __init__(self,name,body):
        self.name = name 
        self.body = body


@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')


@app.route('/blog', methods=['POST', 'GET'] ) 
def blog():    
    blogpost = Blog.query.all()
    blogid = request.args.get('id')
    
    if blogid == None:
        return render_template('index.html',title="Build a blog",blogpost=blogpost) 
    
    else:
        blogpage = Blog.query.get(blogid)
        
        
       
        return render_template('post.html',blogpage=blogpage)
        
        

@app.route('/add', methods = ['POST','GET'])
def newpost():
    newpost_error = ''
    body_error = ''
    
   

    if request.method == "GET":
        return render_template('newpost.html',title='New blog entry')    

    if request.method == 'POST':
        blog_name = request.form['newpost']
        blog_body = request.form['body']

        if blog_name == '':
            newpost_error = 'Insert Title'
    
        if blog_body=='':
            body_error = 'Enter content in body'    
        
        if not newpost_error and not body_error:  
             new_post = Blog(blog_name,blog_body)
             db.session.add(new_post)
             db.session.commit()
             blogid = new_post.id 
             return redirect('/blog?id=' + str(new_post.id))

        else:
            return render_template('newpost.html',title='New blog entry',newpost_error=newpost_error, body_error=body_error)





if __name__ == '__main__':
    app.run()
