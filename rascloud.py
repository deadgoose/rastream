
import requests
from bs4 import BeautifulSoup
import random
import string
import threading
import Queue
import time
import os
import soundcloud
import sys
import subprocess
import sqlite3
conn= sqlite3.connect('db/example.db')
id=open('client_id').readline()
client=soundcloud.Client(client_id=id)
HOME_DIR="/home/pi/Desktop/rastream"
youtube_dict = {}
user_agent_proc = subprocess.Popen(["youtube-dl", "--dump-user-agent"], stdout=subprocess.PIPE)
user_agent = user_agent_proc.communicate()[0][:-1]
print user_agent
class Player:

    def pause(self):
        os.system("bash /home/pi/.config/mpv/pause")
        
    def volume(self, amt):
        if amt > 0:
            os.system('bash volu')
        else:
            os.system('bash vold')
        
    def __init__(self):
        self.current_stream=None
        self.streams = Queue.Queue()
        t = threading.Thread(target=self.start)
        t.start()
        self.running = True

    def get_enqueued(self):
        names = []
        r = self.streams.qsize()
        for i in range(r):
            try:
                names.append(self.streams.queue[i].get_name())
            except:
                if self.current_stream:
                    names.insert(0, self.current_stream.get_name())
                return names
        if self.current_stream:
            names.insert(0, self.current_stream.get_name())
        return names
    
    def add_stream(self,url):
        print 'in parse'
        if 'youtube.com' in url:
            self.add_youtube(url)
        elif 'soundcloud.com' in url:
            self.add_soundcloud(url)
        elif 'youtu.be' in url:
            self.add_youtube(url)

    def add_youtube(self, url):
        sound = YoutubeStream()
        sound.load(url)
        print type(sound)
        self.enqueue(sound)

        

    def add_soundcloud(self, url):
        sc = client.get("/resolve", url=url)
        if sc.kind=='playlist':
            for track in sc.tracks:
                uri = "/tracks/%s"%track['id']
                sound = SoundcloudStream()
                sound.load(uri)
                self.enqueue(sound)
        else:
            uri = "/tracks/%s"%sc.id
            sound = SoundcloudStream()
            sound.load(uri)
            self.enqueue(sound)

        
        
    def enqueue(self, s):
        self.streams.put(s)
        

    def start(self):
        while(True):
            #if not self.running:
            #    return
            s=self.streams.get(block=True)
            self.play_stream(s)
        
    def play_stream(self,s):
        self.current_stream=s
        proc = s.play()
        proc.communicate()
        print 'done!'
        
    def turn_off(self):
        self.stop_stream()
        self.running=False
        
    def stop_stream(self):
        if self.current_stream:
            self.current_stream.stop()
            
class Stream:

    def play(self):
        pass

    def stop(self):
        pass

    def load(self, url):
        pass

    def get_name(self):
        pass
    
class YoutubeStream(Stream):

    def load(self, url):
        self.name = self.get_database(url)
        if self.name:
            print "already downloaded %s, playing!"%self.name
            return
        soup=BeautifulSoup(requests.get(url).text, "lxml")
        self.name = soup.find(class_="watch-title").string
        self.url=url
        #self.youtube_dl = subprocess.Popen(["youtube-dl", "--user-agent= -", url], stdout=subprocess.PIPE)
        self.youtube_dl = subprocess.Popen(["youtube-dl", "--user-agent", user_agent[0][:-1], "--cookies=youtube-dl_mpv.XXXX/cookies", "--get-url", url], stdout=subprocess.PIPE)
        self.youtube_dl_url = None
        t = threading.Thread(target=self.get_youtube_url)
        t.start()
        """all this stuff is useless now!
        self.name = "    Still loading..."#we chop off the yts unconditionally i.e. 4 chars
        dl_name='yts/%(title)s.%(ext)s'
        self.youtube_dl = subprocess.Popen(["youtube-dl", "-x",
                                            "--restrict-filenames",
                                            "-o",
                                            dl_name, url],
                                           stdout=subprocess.PIPE)
        self.url = url
        print "going to download %s!!!"%url
        t = threading.Thread(target=self.set_name)
        t.start()"""
    def get_youtube_url(self):
        url=self.youtube_dl.communicate()[0][:-1]
        self.youtube_dl_url=url
        

        
    def set_name(self):
        
        
        self.name = self.youtube_dl.communicate()[0][:-1]
        if "has already been downloaded" in self.name:
            first = self.name.find("[download]")
            last = self.name.find("has already been downloaded")
            self.name = self.name[first+11:last-1]
        else:
            first = self.name.find("Destination")
            second_first = self.name.find("Destination", first+1)
            if second_first != -1:
                first = second_first
            last = self.name.find('\n', first)
            self.name = self.name[first+13:last]
        my_conn= sqlite3.connect('db/example.db')
        c = my_conn.cursor()
        new_name=self.name.decode('utf-8')
        subprocess.Popen(["mv", self.name, new_name])
        self.name = new_name
        c.execute("INSERT INTO urls VALUES ((?), (?))", (self.url, self.name))
        my_conn.commit()
        my_conn.close()
        
    def play(self):
        while(not self.youtube_dl_url):
            time.sleep(1)
            
        print "rascloud is playing %s"%self.name
        #self.mplayer_proc = subprocess.Popen(["mpv", self.name])
        #self.mplayer_proc = subprocess.check_output(["mpv", "-", "--no-video"], stdin=self.youtube_dl.stdout)
        self.mplayer_proc = subprocess.Popen(["mpv", "--cookies", "--cookies-file=youtube-dl_mpv.XXXX/cookies", "--user-agent", user_agent, "--no-video", self.youtube_dl_url])
        return self.mplayer_proc

    def stop(self):
        self.mplayer_proc.kill()

    def get_name(self):
        return self.name[4:]

    def get_database(self, url):
        my_conn = sqlite3.connect('db/example.db')
        print 'in db'
        c = my_conn.cursor()
        c.execute("SELECT file from urls where url=(?)", (url,))
        r = c.fetchone()
        if r:
            my_conn.close()
            return r[0].encode('ascii', 'ignore')
        my_conn.close()
        return None
        
class SoundcloudStream(Stream):


    def load(self,url):
        self.url = url

        
    def play(self):
        try:
            track = client.get(self.url)
            stream_url = client.get(track.stream_url, allow_redirects=False)
            input_file="%s/download"%HOME_DIR
            with open(os.devnull, 'w') as fp:
                self.wget_proc = subprocess.Popen(["wget", stream_url.location, "-O", input_file], stdout=fp)
            print 'we wget!!'
            #        with open(os.devnull, 'w') as fp:
            self.mplayer_proc = subprocess.Popen(["mplayer", "-really-quiet",input_file])
            return self.mplayer_proc
        except:
            self.mplayer_proc = subprocess.Popen(["echo", "cant stream"])
            return self.mplayer_proc
        
    def stop(self):
        self.wget_proc.kill()
        self.mplayer_proc.kill()
        
    def get_name(self):
        track = client.get(self.url)
        user = track.user["username"]
        return track.title + " - " + user

def random_name():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
if __name__=="__main__":
    p = Player()
    s1 = SoundcloudStream()
    s1.load("https://soundcloud.com/lifeofdesiigner/desiigner-panda")
    s2 = SoundcloudStream()
    s2.load("https://soundcloud.com/wmstrecs/bathtub-fart-booming")
    p.enqueue(s1)
    p.enqueue(s2)
    time.sleep(15)
    p.stop_stream()
    print 'stopped'
