import threading
import Queue
import time
import os
import soundcloud
import sys
import subprocess

id=open('client_id').readline()
client=soundcloud.Client(client_id=id)
HOME_DIR="/home/pi/rastream"


class Player:


    def __init__(self):
        self.current_stream=None
        self.streams = Queue.Queue()
        t = threading.Thread(target=self.start)
        t.start()
        self.running = True

    def get_enqueued(self):
        names = []
        return names
        r = self.streams.qsize()
        for i in range(r):
            try:
                names.append(self.streams.queue[i].url)
            except:
                return names
        return names
    
    def add_stream(self,url):
        print 'in parse'
        sc = client.get("/resolve", url=url)
        print 'hey'
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

    def play():
        pass

    def stop():
        pass
    
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
