from searcher import Searcher
from flask import Flask
from flask import request, session, redirect, url_for, escape, render_template
import rascloud
import cheat_stream
app = Flask(__name__)
player = rascloud.Player()
f = open('flask_config', 'r')
u_and_p = f.readline()
my_username = u_and_p.split()[0]
my_password = u_and_p.split()[1]
f.close()

@app.route('/vid_stream', methods=['POST'])
def vid_stream():
    vid_stream=cheat_stream.get(request.form['vid_stream'])
    print vid_stream
    ret= '''
    <a href='''+vid_stream+'''>click</a>'''
    return render_template('vid_stream.html', vs=vid_stream)

@app.route('/pause', methods=['POST'])
def pause():
    player.pause()
    return redirect(url_for('queue'))

@app.route('/')
def hello_world():
    return "Hello world!"

@app.route('/volu', methods=['POST'])
def volu():
    player.volume(1)
    return redirect(url_for('queue'))

@app.route('/vold', methods=['POST'])
def vold():
    player.volume(-1)
    return redirect(url_for('queue'))

@app.route('/skip')
def skip():
    if is_logged_in():
        player.stop_stream()
        return redirect(url_for('queue'))
    else:
        return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method=='GET':
        return redirect(url_for('queue'))
    search = Searcher(request.form['search'])
    yt_res = search.get_res()
    return render_template('search.html', yt=yt_res[:5], search=request.form['search'], is_logged_in = is_logged_in())
    
@app.route('/queue', methods=['GET', 'POST'])
def queue():
    print 'hello'
    if request.method=='POST':
        if is_logged_in():
            print request.form['stream']
            player.add_stream(request.form['stream'])


    if 'url' in request.args and is_logged_in():
        url = request.args['url']
        if 'list' in request.args:
            url+='%list='+request.args['list']
        print url
        player.add_stream(url)
        return redirect(url_for('queue'))
    ret= '''
        <form action="search" method="post">
            <p><input type=text name=search></p>
            <p><input type=submit value=Search></p>
        </form>
        <form action="" method="post">
            <p><input type=text name=stream></p>
            <p><input type=submit value=Queue></p>
        </form>
        <a href="/skip">Skip current track</a>
    '''
    songs = player.get_enqueued()
    if len(songs) > 0:
        ret+='''<ol>'''
        for name in songs:
            ret+='''<li>'''
            ret+= name
            ret+='''</li>'''
        ret+='''</ol>'''
    #return ret
    
    return render_template('queue.html', songs=songs, is_logged_in = is_logged_in())

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
    if is_logged_in():
        return redirect(url_for('queue'))
    return render_template('login.html', error=error, is_logged_in = is_logged_in())
    ret= '''
        <form action="" method="post">
            <p><input type=text name=username></p>
            <p><input type=text name=password></p>
            <p><input type=submit value=Submit></p>
        </form>
    '''
    return ret
    
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
    if 'username' in session and session['username'] == my_username:
        return True
    return False

if __name__=="__main__":
    f = open('flask_secret', 'r')
    app.secret_key = f.readline()
    f.close()
    #app.debug=True
    app.run(host='0.0.0.0')



