from flask import Flask
from flask import request, session, redirect, url_for, escape
import rascloud
app = Flask(__name__)
player = rascloud.Player()
f = open('flask_config', 'r')
u_and_p = f.readline()
my_username = u_and_p.split()[0]
my_password = u_and_p.split()[1]
print my_password
print my_username
f.close()

@app.route('/')
def hello_world():
    return "Hello world!"


@app.route('/skip')
def skip():
    if is_logged_in():
        player.stop_stream()
        return redirect(url_for('queue'))
    else:
        return redirect(url_for('login'))
@app.route('/queue', methods=['GET', 'POST'])
def queue():
    if request.method=='POST':
        if is_logged_in():
            print request.form['stream']
            player.add_stream(request.form['stream'])

                
    ret= '''
        <form action="" method="post">
            <p><input type=text name=stream>
            <p><input type=submit value=Queue>
        </form>
        <a href="/skip">Skip current track</a>
    '''
    songs = player.get_enqueued()
    print songs
    if len(songs) > 0:
        ret+='''<ol>'''
        for name in songs:
            ret+='''<li>'''
            ret+= name
            ret+='''</li>'''
        ret+='''</ol>'''
    return ret

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        print request.form['username']
        print request.form['password']
        if valid_login(request.form['username'], request.form['password']):
            print 'valid'
            return log_in_user(request.form['username'])
        else:
            print 'failed'
            error='Invalid login credentials'
    #render_template('login.html', error=error)
    return '''
        <form action="" method="post">
            <p><input type=text name=username>
            <p><input type=text name=password>
            <p><input type=submit value=Login>
        </form>
    '''
    
def log_in_user(user):
    session['username'] = request.form['username']
    print 'sessions'
    return redirect(url_for('queue'))

def valid_login(user, password):
    print 'valid login?'
    print '---'
    print my_username
    print my_password
    print '---'
    if user==my_username and password==my_password:
        return True
    return False

def is_logged_in():
    print 'checking if logged in'
    print escape(session['username'])
    if session['username'] == my_username:
        return True
    return False

if __name__=="__main__":
    f = open('flask_secret', 'r')
    app.secret_key = f.readline()
    f.close()
    #app.debug=True
    app.run()



