# Store this code in 'app.py' file

from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import base64
import random
import datetime
import os
import string
import operator
import spacy
nlp = spacy.load('en_core_web_sm')

app = Flask(__name__,static_folder='static')


app.secret_key = 'your secret key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'swanDB2'
app.config['UPLOAD_FOLDER'] = "static/uploads"

mysql = MySQL(app)


@app.route('/')
def first():
	return render_template('pages-login.html', msg = '')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = %s', (username,))
        user = cursor.fetchone()

        if user is None:
            flash("User does not exist")
            return redirect(url_for('login'))
        

        if user['password'] != password :
            flash("Incorrect password")
            return redirect(url_for('login'))
    
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        account = cursor.fetchone()
        
        if account:
            session['loggedin'] = True
            session['id'] = account['user_id']
            session['username'] = account['username']
            msg = 'Logged in successfully!'
            return redirect(url_for('index'))
        else:
            msg = 'Incorrect username / password!'
            
    return render_template('pages-login.html', msg=msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('first'))

@app.route('/register', methods =['GET', 'POST'])
def register():
	msg = ''
	# return render_template('pages-register.html', msg = msg)

	if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
		username = request.form['username']
		password = request.form['password']
		email = request.form['email']
		cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute('SELECT * FROM accounts WHERE username = % s', (username, ))
		account = cursor.fetchone()
		if account:
			msg = 'Account already exists !'
		elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
			msg = 'Invalid email address !'
		elif not re.match(r'[A-Za-z0-9]+', username):
			msg = 'Username must contain only characters and numbers !'
		elif not username or not password or not email:
			msg = 'Please fill out the form !'
		else:
			cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s,NULL)', (username, password, email, ))
			mysql.connection.commit()
			msg = 'You have successfully registered !'
            


	elif request.method == 'POST':
		msg = 'Please fill out the form !'
	return render_template('pages-register.html', msg = msg)

# @app.route('/<int:User_ID>/profile',methods=['GET'])   ########
# def profile(User_ID):
#     # Check if user is loggedin
    
#     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
#     cursor.execute('SELECT * FROM accounts WHERE User_ID = %s', (User_ID,))
#     account = cursor.fetchone() 
#     # Show the profile page with account info
#     return render_template('users-profile.html', account=account)

def sortt(acc,user_id,l3):
    #l1=list(acc)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    l2=[]
    #l2.append(l3)
    print("jajaja")
    print(l3)
    for e in acc:
        if(e['community_id'] in l3):
            # cursor.execute('SELECT * FROM posts WHERE community_id = %s',(e['community_id'],))
            # a=cursor.fetchall()
            print(type(e))
            l2.append(e)

    cursor.execute('SELECT * FROM comment_count WHERE user_id = %s',(user_id,))
    a=cursor.fetchone()
    if(a is None):
        #bias
        cursor.execute('SELECT * FROM trend_count')
        a=list(cursor.fetchall())
        nwlst = sorted(a, key=operator.itemgetter('tratio'), reverse=True)
        for e in nwlst:
            if(e['community_id'] in l3):
                continue
            cursor.execute('SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id WHERE communities.community_id = %s',(e['community_id'],))
            # cursor.execute('SELECT * FROM posts WHERE community_id = %s',(e['community_id'],))
            a=cursor.fetchall()
            l2+=(list(a))


    else:
        l4=[]
        cursor.execute('SELECT * FROM comment_count WHERE user_id = %s',(user_id,))
        a=list(cursor.fetchall())
        nwlst = sorted(a, key=operator.itemgetter('comments_count'), reverse=True)
        for e in nwlst:
            if(e['community_id'] in l3):
                continue
            cursor.execute('SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id WHERE communities.community_id = %s',(e['community_id'],))
            # cursor.execute('SELECT * FROM posts WHERE community_id = %s',(e['community_id'],))
            a=cursor.fetchall()
            l4.append(e['community_id'])
            l2+=(list(a))
        
        cursor.execute('SELECT * FROM trend_count')
        a=list(cursor.fetchall())
        nwlst = sorted(a, key=operator.itemgetter('tratio'), reverse=True)
        for e in nwlst:
            if(e['community_id'] in l3):
                continue
            if(e['community_id'] in l4):
                continue
            cursor.execute('SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id WHERE communities.community_id = %s',(e['community_id'],))
            a=cursor.fetchall()
            l2+=(list(a))

    return tuple(l2)

@app.route('/index')              ##########
def index():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id=session['id']
    # print(user_id)
    # print("heheheheheheheheheheheheh")
    cursor.execute('SELECT * FROM accounts WHERE user_id = %s',(user_id,))
    # print("jjsnnhjsnkjsnvjsnkvjnsvj")
    a=cursor.fetchone()
    # print(a)
    usrnm=a['username']
    cursor.execute('SELECT * FROM communities WHERE owned_by=%s',(usrnm,))
    a=cursor.fetchall()
    # print(a)
    lst=[]#list of my created communities
    for e in a:
        lst.append(e['community_id'])
    # print(lst)
    # print(user_id)
    # print("hehehehheeheheheeheheheheh")
    # SELECT * FROM posts ORDER BY community ASC, id DESC
    cursor.execute('SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id')
    acc = cursor.fetchall() 
    # print(type(acc[0]))
    # print(acc)

    ac1=sortt(acc,user_id,lst)
    # print("heheheheheheheheheheh")
    # print(ac1)

    # print(acc[0])
    # print("hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh")
    # print(ac1[0])

    cursor.execute('SELECT * FROM comments')
    com = cursor.fetchall() 


   

    return render_template('index.html', posts=ac1,comments=com)


@app.route('/profile/<int:user_id>',methods=['GET','post'])   ########
def profile(user_id):
    # Check if user is loggedin
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if session['id']==user_id:
        cursor.execute('SELECT * FROM accounts WHERE user_id = %s', (user_id,))
        account = cursor.fetchone()

        # Show the profile page with account info
        return render_template('users-profile.html', account=account,pt=user_id)
    else:
        if(request.method =='GET'):

            cursor.execute(f'SELECT * from posts WHERE user_id = {user_id}')
            posts = cursor.fetchall()
  
            cursor.execute(f'SELECT * from accounts WHERE user_id = {user_id}')
            user = cursor.fetchone()
            username=user['username']
            cursor.execute(f'SELECT * from comments')
            comments = cursor.fetchall()
   
            cursor.execute(f'select * from comuser where user_id={user_id}')
            communities = cursor.fetchall()
            return render_template('single-user.html',posts=posts,comments=comments,comuser=communities,pt=user_id,username=username)
        else:
            current_user = session['id']
            cursor.execute(f'select * from friends where friend_id="{user_id}" and user_id="{current_user}"')
            result = cursor.fetchone()
            mysql.connection.commit()
            cursor.execute(f'SELECT * from posts WHERE user_id = {user_id}')
            posts = cursor.fetchall()
            cursor.execute(f'SELECT * from comments')
            comments = cursor.fetchall()
            cursor.execute(f'select * from comuser where user_id={user_id}')
            communities = cursor.fetchall()
            cursor.execute(f'SELECT * from accounts WHERE user_id = {user_id}')
            user = cursor.fetchone()
            username=user['username']
            if(result!=None):
                flash("already a friend")
                return render_template('single-user.html',posts=posts,comments=comments,comuser=communities,pt=user_id,username=username)
            
            cursor.execute(f'select * from accounts where user_id="{user_id}"')
            details = cursor.fetchone()
            friendname = details['username']
            cursor.execute('insert into friends (friend_id,user_id,friendname,friendprofile) values(%s,%s,%s,%s)',(user_id,session['id'],friendname,details['profile']))
            mysql.connection.commit()

            return render_template('single-user.html',posts=posts,comments=comments,comuser=communities,pt=user_id,username=username)
          
             
@app.route('/<int:user_id>/profile/myfriends',methods=['GET','delete'])                        ###########
def myfriends(user_id):

    if request.method == 'GET':
        # We need all the account info for the user so we can display it on the profile page

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM friends WHERE user_id = %s', (user_id,))
		
        myfriend = cursor.fetchall()
        # Show the profile page with account info
        return render_template('myfriends.html', myfriend=myfriend)



    # elif request.method == 'POST':
    #     # Form is empty... (no POST data)
    #     msg = 'Please fill out the form!'
    #     # Show registration form with message (if any)
    #     return render_template('myfriends.html',msg=msg)

    return render_template('myfriends.html')


@app.route('/community/<int:community_id>',methods=['GET', 'DELETE','post'])       #############
def singlecommunity(community_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'GET':
        cursor.execute(f'SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id where posts.community_id= {community_id}')
        posts = (cursor.fetchall())
	
        cursor.execute(f'SELECT * FROM comments LEFT JOIN posts on comments.post_id = posts.post_id where community_id= {community_id}')
        comments=cursor.fetchall()
	
        cursor.execute(f'SELECT * FROM comuser where community_id= {community_id}')
        users=cursor.fetchall()
	
        
        return render_template('single-community.html', comments=comments,posts=posts,comuser=users,communityname=users[0]['communityname'],pt=users[0]['community_id'])
       
    elif request.method == 'DELETE':

        if 'loggedin' not in session:

            msg ='You are not logged in'

            return render_template('single-community.html',msg=msg)

        cursor.execute('SELECT owner FROM communities where community_ID= %s',(community_id))
        owner = cursor.fetchall()

        if owner != session['id']:
            msg ='cannot delete this post'

            return render_template('singlecommunity.html',msg=msg)

        cursor.execute('DELETE FROM communities where community_ID= %s',(community_id))

        return redirect(url_for('index'))
    
    cursor.execute(f'select * from comuser where community_id="{community_id}" and user_id = {session["id"]}')
    result = cursor.fetchone()
    cursor.execute(f'SELECT * FROM posts where community_id= {community_id}')
    posts = (cursor.fetchall())

    cursor.execute(f'SELECT * FROM comments LEFT JOIN posts on comments.post_id = posts.post_id where community_id= {community_id}')
    comments=cursor.fetchall()

    cursor.execute(f'SELECT * FROM comuser where community_id= {community_id}')
    users=cursor.fetchall()
	
    if(result != None):
        flash("already joined")
        return render_template('single-community.html', comments=comments,posts=posts,comuser=users,communityname=users[0]['communityname'],pt=users[0]['community_id'])
            

    cursor.execute(f'select * from communities where community_id="{community_id}"')
    name = cursor.fetchone()
    communityname = name['communityname']

    user=session['id']
    cursor.execute(f'select * from accounts where user_id="{user}"')
    oops = cursor.fetchone()

    print(oops)

    cursor.execute('insert into comuser (user_id , community_id, communityname , username,profile) values (%s,%s,%s,%s,%s)',(session['id'],community_id,communityname,session['username'],oops['profile']))
    mysql.connection.commit()


    return render_template('single-community.html', comments=comments,posts=posts,comuser=users,communityname=users[0]['communityname'],pt=users[0]['community_id'])



@app.route('/index/<string:titu>') 
def otherprofile(titu):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id=session['id']
    # print(user_id)
    # print("heheheheheheheheheheheheh")
    cursor.execute('SELECT * FROM accounts WHERE user_id = %s',(user_id,))
    # print("jjsnnhjsnkjsnvjsnkvjnsvj")
    a=cursor.fetchone()
    # print(a)
    usrnm=a['username']
    cursor.execute('SELECT * FROM communities WHERE owned_by=%s',(usrnm,))
    a=cursor.fetchall()
    # print(a)
    lst=[]#list of my created communities
    for e in a:
        lst.append(e['community_id'])

    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id where posts.genre = "{titu}" ')
    posts = cursor.fetchall()
    posts1 = sortt(posts,user_id,lst)

    
 
    cursor.execute(f'SELECT * FROM comments LEFT JOIN posts on comments.post_id = posts.post_id where genre="{titu}"')
    comments=cursor.fetchall()

    return render_template('otherprofile.html',posts=posts1,comments=comments,genre=titu)


@app.route('/posts/<int:post_id>',methods=['GET','POST', 'DELETE'])       #############
def singlepost(post_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'SELECT * FROM posts where post_id= "{post_id}"')
    post = cursor.fetchall()
    cursor.execute(f'SELECT * FROM comments where post_id="{post_id}"')
    com = cursor.fetchall() 

    if request.method == 'GET':

     

        return render_template('singlepost.html', posts=post,comments=com,pt=post_id)
    
    elif request.method == 'POST':
         
        user_id=session['id']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'select * from accounts where user_id={user_id}')
        details=cursor.fetchall()

        username=details[0]['username']
        profile=details[0]['profile']
        Datas = request.form['comment'] 

        if Datas == '':
             
            flash("please fill out the form")
            return render_template('singlepost.html',posts=post,comments=com,pt=post_id)
             


        #increment comment count
        #update trend_count

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM posts where post_id= "{post_id}"')
        detail1=cursor.fetchone()

        user_id = session['id']
        community_id =detail1['community_id']
        # cursor.execute(f'SELECT * FROM commentcount where user_id= "{user_id}" and community_id="{community_id}"')
        # detail1=cursor.fetchall()
        commcount=1
        # if(detail1 is not []):
        #     commcount = detail1[0][2]
        
        # cursor.execute('insert into comuser (user_id , community_id, communityname , username) values (%s,%s,%s,%s)',(session['id'],community_id,communityname,session['username']))
        # mysql.connection.commit()
        cursor.execute('SELECT * FROM comment_count WHERE user_id = %s AND community_id = %s', (user_id, community_id))
        # cursor.execute(f'SELECT * FROM commentcount where user_id= "{user_id}" and community_id="{community_id}"')
        detail1=cursor.fetchone()
        # print(type(detail1))
        # print("check above")
        if(detail1!=None):
            # print("hhhhh")
            cursor.execute('UPDATE comment_count SET comments_count = comments_count + %s WHERE user_id = %s AND community_id = %s', (1,user_id, community_id,))
        
            mysql.connection.commit()
            # update_statement = "UPDATE commentcount SET comments_count = comments_count + %s WHERE user_id = %s AND community_id = %s"
            # cursor.execute(update_statement, (commcount, user_id, community_id))
            # mysql.connection.commit()
        else:
            # print("bbbbbb")
            insert_statement = "INSERT INTO comment_count (user_id, community_id, comments_count) VALUES (%s, %s, %s)"
            cursor.execute(insert_statement, (user_id, community_id, commcount))
            mysql.connection.commit()


        cursor.execute('SELECT * FROM trend_count WHERE community_id = %s', (community_id,))
        detail1=cursor.fetchone()

        if(detail1==None):
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('SELECT * from communities where community_id=%s',(community_id,))
            a=cursor.fetchone()
            communityname=a['communityname']
            cursor.execute('SELECT * from posts where community_id=%s',(community_id,))
            a=cursor.fetchall()
            posts_no=len(a)

            cc=0
            for e in a:
                postid=e['post_id']
                cursor.execute('SELECT * from comments where post_id=%s',(postid,))
                ab=cursor.fetchall()
                cc+=len(ab)

            cursor.execute('SELECT * from comuser where community_id=%s',(community_id,))
            a=cursor.fetchall()
            tot_user=len(a)

            tratio=(0.5)*(cc+1/posts_no)+(0.3)*(cc+1)+(0.2)*(cc+1/tot_user)
            cursor.execute('INSERT INTO trend_count (community_id,communityname, posts_no, tot_user,comments_count,tratio) VALUES (%s, %s, %s, %s,%s,%s)', (community_id, communityname, 1, tot_user,cc+1,tratio,))
            mysql.connection.commit()
        else:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute(f'SELECT * FROM trend_count where community_id= "{community_id}"')
            detail1=cursor.fetchone()
            posts_no=detail1['posts_no']
            cc=detail1['comments_count']
            tratio=(0.5)*(cc+1/posts_no)+(0.3)*(cc+1)+(0.2)*(cc+1/detail1['tot_user'])
            cursor.execute('UPDATE trend_count SET tratio=%s,comments_count=comments_count+%s WHERE community_id = %s', (tratio,1,community_id,))
            mysql.connection.commit()


        cursor.execute('insert into comments (post_id , user_id, Datas ,username,profile) values (%s,%s,%s,%s,%s)',(post_id,user_id,Datas,username,profile))
        mysql.connection.commit()

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM posts where post_id= "{post_id}"')
        post = cursor.fetchall()
        cursor.execute(f'SELECT * FROM comments where post_id="{post_id}"')
        com = cursor.fetchall() 

        request.form=([])
        # cursor.execute('insert into comments (post_id , user_id, Datas , username,profile) values (%s,%s,%s,%s,%s)',(post_id,user_id,Datas,username,profile))
        # mysql.connection.commit()

        # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # cursor.execute(f'SELECT * FROM posts where post_id= "{post_id}"')
        # post = cursor.fetchall()
        # cursor.execute(f'SELECT * FROM comments where post_id="{post_id}"')
        # com = cursor.fetchall() 

        # request.form=([])

        

        return render_template('singlepost.html',posts=post,comments=com,pt=post_id)
    
    return render_template('singlepost.html',posts=post,comments=com,pt=post_id,)




    # elif request.method == 'DELETE':

    #     if 'loggedin' not in session:

    #         msg ='You are not logged in'

    #         return render_template('singlepost.html',msg=msg)

    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('SELECT id FROM posts where Post_ID= %s',(Post_ID))
    #     owner = cursor.fetchall()

    #     if owner != session['id']:
    #         msg ='cannot delete this post'

    #         return render_template('singlepost.html',msg=msg)

    #     cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #     cursor.execute('DELETE FROM posts where Post_ID= %s',(Post_ID))

    #     return redirect(url_for('home'))

    # return redirect(url_for('home'))



@app.route('/<int:user_id>/setting',methods=['GET','POST'])       ######
def setting(user_id):

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE user_id = %s', (user_id,))
    account = cursor.fetchall()

    # Show the profile page with account info
    return render_template('user-profilesetting.html', account=account)

@app.route('/myposts/<int:user_id>',methods=['GET', 'DELETE'])       #############
def mypost(user_id):

    if request.method == 'GET':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT post_id,user_id,datas,posts.community_id,genre,postname,image_path,communityname FROM posts left join communities on posts.community_id=communities.community_id where user_id= "{user_id}"')
        post = cursor.fetchall()
        cursor.execute(f'SELECT * from comments')
        com = cursor.fetchall() 

        return render_template('mypost.html', posts=post,comments=com)
    
@app.route('/mycommunities/<int:user_id>',methods=['GET', 'DELETE'])       #############
def mycommunities(user_id):

    if request.method == 'GET':

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'SELECT * FROM comuser where user_id= "{user_id}"')
        comuser = cursor.fetchall()

        return render_template('mycommunity.html', comuser=comuser)
    
def render_picture(data):

    render_pic = base64.b64encode(data).decode('utf-8') 
    return render_pic
    
@app.route('/createpost', methods=['GET', 'POST'])
def createpost():
    if request.method == 'POST':
        communityname = request.form['communityname']        
        image=request.files["img"]
        # img_data=image.read()
        # render_file = render_picture(img_data)


        datas = request.form['datas']
        genre = request.form['genre']
        postname = request.form['postname']
        user_id = session['id']

        filepath = ""

        if image:
            # Generate a random string to append to the filename
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Get the current timestamp to append to the filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            ext = image.filename.split('.')[-1]
            filename = f"{random_string}-{timestamp}.{ext}"
            # Save the file to the server with the new filename
            upload_directory = os.path.join(app.config['UPLOAD_FOLDER'],"posts")

            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)

            filepath = os.path.join(upload_directory, filename)
            image.save(filepath)
            filepath = filepath[7:]
            # Save the filepath to the MySQL database

        if not communityname or not datas or not genre or not postname:
            flash("please fill out the form")
            return redirect(url_for('createpost'))

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute(f'select * from communities where communityname="{communityname}"')
        user = cursor.fetchone()

        if user is None:
            flash("Community does not exist")
            return redirect(url_for('createpost'))

        cursor.execute(f'select community_id from communities where communityname="{communityname}"')
        comid = cursor.fetchall()
        community_id = comid[0]['community_id']

        cursor.execute('INSERT INTO posts (community_id, user_id, datas, genre,postname,image_path) VALUES (%s, %s, %s, %s,%s,%s)', (community_id, user_id, datas, genre,postname,filepath))
        mysql.connection.commit()

        ###
        cursor.execute('select * from trend_count where community_id=%s', (community_id,))
        a=cursor.fetchone()
        if(a is None):
            posts_no=0
        else:
            posts_no=a['posts_no']

        cursor.execute('select * from comuser where community_id=%s', (community_id,))
        a=cursor.fetchall()
        tot_user=len(a)

        # cursor.execute('INSERT INTO posts (community_id, user_id, datas, genre,postname) VALUES (%s, %s, %s, %s,%s)', (community_id, user_id, datas, genre,postname,))
        # mysql.connection.commit()

        #insert into trend_count
        cursor.execute('select * from trend_count where community_id=%s', (community_id,))
        a=cursor.fetchone()
        if(a is None):
            posts_no=0
            cursor.execute('INSERT INTO trend_count (community_id,communityname, posts_no, tot_user,comments_count,tratio) VALUES (%s, %s, %s, %s,%s,%s)', (community_id, communityname, 1, tot_user,0,0,))
            mysql.connection.commit()
        else:
            posts_no=a['posts_no']
            cc=a['comments_count']
            tratio=(0.5)*(cc/posts_no+1)+(0.3)*(cc)+(0.2)*(cc/a['tot_user'])
            cursor.execute('UPDATE trend_count SET posts_no=posts_no + %s,tratio=%s WHERE community_id = %s', (1,tratio,community_id,))
            mysql.connection.commit()

        return redirect(url_for('index'))
    return render_template('createpost.html')




@app.route('/createcommunity', methods=['GET', 'POST'])
def createcommunity():

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':

        communityname = request.form['communityname']
        community_id = request.form['community_id']

        if not communityname or not community_id:
            flash("Please fill out the form")
            return redirect(url_for('createcommunity'))
        
        cursor.execute(f'select * from communities where communityname= "{communityname}"')
        comm = cursor.fetchone()

        if comm!= None:
            flash("Community already exists !")
            return redirect(url_for('createcommunity'))

        cursor.execute(f'select * from communities where community_id= "{community_id}"')
        com = cursor.fetchone()

        if com!= None:
            flash("Community ID already taken !")
            return redirect(url_for('createcommunity'))
        
    

        user_id = session['id']
        
        cursor.execute(f'select * from accounts where user_id={user_id}')
        details = cursor.fetchall()

        cursor.execute('INSERT INTO communities (communityname, community_id, owned_by) VALUES (%s ,%s ,%s)', (communityname, community_id, session['username']))
        mysql.connection.commit()

        cursor.execute(f'select * from communities')
        comm = cursor.fetchall()
    

        cursor.execute('insert into comuser (communityname, community_id, username, user_id,profile) values (%s,%s,%s,%s,%s)', (communityname, community_id, details[0]['username'], user_id,details[0]['profile']))
        mysql.connection.commit()

        cursor.execute(f'select * from comuser')
        comu = cursor.fetchall()


        return redirect(url_for('index'))

    return render_template('createcommunity.html')






@app.route('/<int:user_id>/setting/changepassword',methods=['GET','POST'])       #NOPE#
def changepassword(user_id):

    if request.method == 'GET' :
        return render_template('user-profilesetting.html')

    else:

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(f'select * from accounts where user_id={user_id}')
        details=cursor.fetchall()
        curpass=details[0]['password']

        password = request.form['password']
        newpassword = request.form['newpassword']
        renewpassword= request.form['renewpassword']


        if not password or not newpassword or not renewpassword:
            flash("Please fill out the form")
            return render_template('user-profilesetting.html')


        
        if(curpass!=password):

            flash("Enter correct password")
            return render_template('user-profilesetting.html')

        if(newpassword!=renewpassword):
             
            flash("Both new entered password should match")
            return render_template('user-profilesetting.html')
             

        

        

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE accounts SET password = %s  WHERE user_id = %s AND password = %s', (newpassword, user_id, password,))
        mysql.connection.commit()
        # Fetch one record and return result

        return render_template('user-profilesetting.html')
    
@app.route('/<int:user_id>/setting/editprofile',methods=['GET','POST'])       #NOPE#
def editprofile(user_id):

    if request.method == 'GET' :
        return render_template('user-profilesetting.html')

    else:


        profile=request.files["profile_img"]

        filepath = ""

        if profile:
            # Generate a random string to append to the filename
            random_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            # Get the current timestamp to append to the filename
            timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
            ext = profile.filename.split('.')[-1]
            filename = f"{random_string}-{timestamp}.{ext}"
            # Save the file to the server with the new filename
            upload_directory = os.path.join(app.config['UPLOAD_FOLDER'],"userimg")

            if not os.path.exists(upload_directory):
                os.makedirs(upload_directory)

            filepath = os.path.join(upload_directory, filename)
            profile.save(filepath)
            filepath = filepath[7:]
            # Save the filepath to the MySQL database

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        username = request.form['newname']
        email = request.form['email']

        cursor.execute(f'select * from accounts where user_id = "{user_id}" ')
        account = cursor.fetchone()

        if not username or not email:
            flash("Please fill out the form")
            return render_template('user-profilesetting.html',account=account)
        
        cursor.execute(f'select * from accounts where username = "{username}" ')
        omm = cursor.fetchone()

        if omm!=None:
            flash("Username already exits !")
            return render_template('user-profilesetting.html',account=account)
             
             

        cursor.execute('UPDATE accounts SET username = %s, email = %s ,profile= %s WHERE user_id = %s ', (username,email,filepath, user_id))
        mysql.connection.commit() 

        cursor.execute('UPDATE comuser SET username = %s  WHERE user_id = %s ', (username, user_id,))
        mysql.connection.commit() 

        cursor.execute('UPDATE communities SET owned_by = %s  WHERE owned_by = %s ', (username ,username,))
        mysql.connection.commit() 

        cursor.execute('UPDATE friends SET friendname = %s  WHERE friend_id = %s ', (username, user_id,))
        mysql.connection.commit()    

        cursor.execute('UPDATE comments SET username = %s ,profile= %s  WHERE user_id = %s ', (username,filepath, user_id))
        mysql.connection.commit()   

        cursor.execute(f'select * from accounts where user_id = "{user_id}" ')
        account = cursor.fetchone()

        return render_template('user-profilesetting.html',account=account)
    


####################################################    
@app.route('/<int:post_id>/deletemypost',methods=['get','DELETE'])
def deletemypost(post_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    #update trend_count
    cursor.execute('SELECT * from comments where post_id=%s',(post_id,))
    a=cursor.fetchall()
    l=len(a)
    cursor.execute('SELECT * from posts where post_id=%s',(post_id,))
    a=cursor.fetchone()
    community_id=a['community_id']
    cursor.execute('SELECT * from trend_count where community_id=%s',(community_id,))
    a=cursor.fetchone()
    posts_no=a['posts_no']
    cc=a['comments_count']
    if cc==1:
        cursor.execute(f'Delete from trend_count where community_id="{community_id}"')
        mysql.connection.commit()
    else:
        tratio=(0.5)*(cc-l/posts_no-1)+(0.3)*(cc-l)+(0.2)*(cc-l/a['tot_user'])
        cursor.execute('UPDATE trend_count SET posts_no=posts_no-%s ,comments_count=comments_count-%s , tratio=%s where community_id=%s',(1,l,tratio,community_id,))
        mysql.connection.commit()


    cursor.execute(f'Delete from posts where post_id="{post_id}"')
    mysql.connection.commit()
    return redirect(url_for('mypost',user_id=session['id']))
####################################################

@app.route('/<int:friend_id>/removefriend',methods=['get','DELETE'])
def removefriend(friend_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    user_id = session['id']
    cursor.execute(f'Delete from friends where friend_id="{friend_id}" and user_id="{user_id}"')
    mysql.connection.commit()
    return redirect(url_for('myfriends',user_id=session['id']))

@app.route('/<int:community_id>/removecommunity',methods=['get','DELETE'])
def removecommunity(community_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'Delete from comuser where community_id="{community_id}" and user_id={session["id"]}')
    mysql.connection.commit()

    cursor.execute(f'select * from communities where community_id="{community_id}"')
    details=cursor.fetchone()

    if(details['owned_by']== session["username"]):
        cursor.execute(f'Delete from communities where community_id="{community_id}"')
        mysql.connection.commit()



    return redirect(url_for('mycommunities',user_id=session['id']))




@app.route('/finduser',methods=['POST'])
def find_user():
     
    username = request.form['user_name']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'select * from accounts where username="{username}"')
    user = cursor.fetchone()
    if user is None:
        flash("User does not exist")
        return redirect(url_for('index'))
    user_id = user['user_id']
    return redirect(url_for('profile',user_id=user_id))

@app.route('/findcommunity',methods=['POST'])
def find_community():
     
    communityname = request.form['communityname']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(f'select * from communities where communityname="{communityname}"')
    user = cursor.fetchone()
    if user is None:
        flash("Community does not exist")
        return redirect(url_for('index'))
    community_id = user['community_id']
    return redirect(url_for('singlecommunity',community_id=community_id))


@app.route('/findpost',methods=['POST'])
def find_post():
    #here spaCy is used 
    postname = request.form['post_name']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Use spaCy to search for posts based on their meaning or related keywords
    doc = nlp(postname)
    keywords = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'VERB', 'ADJ']]
    #
    # query = postname
    # # Use spaCy's Similarity model to find similar posts
    # #making posts_content
    # cursor.execute('select * from posts')
    # a=list(cursor.fetchall())
    # posts_content=[]
    # for e in a:
    #     posts_content.append(e['datas'])
    #     posts_content.append(e['postname'])

    # posts1 = []
    # for doc1 in nlp.pipe(posts_content):
    #     similarity_score = doc1.similarity(nlp(query))
    #     if similarity_score > 0.5:
    #         posts1.append(doc1.text)

    # print("jahgavdhabdkhadnakjdnakjdnkjdn")
    # print(posts1)
    # posts3=[]
    posts2=[token.lemma_ for token in doc]
    for e1 in keywords:
        if e1 in posts2:
            continue
        else:
            posts.append(e1)
    # Build a query that matches any post containing any of the keywords
    # query = ' OR '.join([f'datas LIKE "%{keyword}%" OR postname LIKE "%{keyword}%"' for keyword in posts2])
    # print("hbhkbhknkjnjlmklmlkmk")
    # print(query)

    #cursor.execute(f'select * from posts where {query}')
    # posts2+=keywords
    print(posts2)
    posts=[]
    for keyword in posts2:
        cursor.execute(f'select * from posts where datas LIKE "%{keyword}%" OR postname LIKE "%{keyword}%"')
        ab1=list(cursor.fetchall())
        for k12 in ab1:
            if k12 in posts:
                continue
            else:
                posts.append(k12)
        #posts+=(list(cursor.fetchall()))
    # cursor.execute(f'select * from posts where datas LIKE "%{keyword}%" OR postname LIKE "%{keyword}%"' for keyword in keywords)
    # posts = cursor.fetchall()

    if posts==[]:
        print("checkcheckcheck")
        flash("Posts do not exist")
        return redirect(url_for('index'))


    comments=[]
    for e in posts:
        cursor.execute('SELECT * FROM comments LEFT JOIN posts on comments.post_id =%s',(e['post_id'],) )
        comments+=(list(cursor.fetchall()))

    posts=tuple(posts)
    comments=tuple(comments)

    return render_template('otherprofile.html', posts=posts, comments=comments, genre='Similar Posts')


    ########
    # postname = request.form['post_name']
    # cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    # cursor.execute(f'select * from posts where postname REGEXP "[a-zA-Z0-9]*{postname}[a-zA-Z0-9]*"')
    # posts = cursor.fetchall()
    # if posts is None:
    #     flash("Posts does not exist")
    #     return redirect(url_for('index'))

    # cursor.execute(f'SELECT * FROM comments LEFT JOIN posts on comments.post_id = posts.post_id where postname REGEXP "[a-zA-Z0-9]*{postname}[a-zA-Z0-9]*"')
    # comments=cursor.fetchall()

    # return render_template('otherprofile.html',posts=posts,comments=comments,genre='Similar Posts')



    
if __name__=="__main__":
    
    app.run(debug=True,port=9000)

