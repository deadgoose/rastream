import soundcloud
import sys
import subprocess

def play_track(url):
    f = open('client_id')
    id=f.readline()
    client=soundcloud.Client(client_id=id)
    track = client.get('/resolve', url=url)
    stream_url = client.get(track.stream_url, allow_redirects=False)
    arg="wget '%s' -O - | mplayer -"%stream_url.location
    subprocess.call(arg, shell=True)

if __name__=="__main__":
    play_track(sys.argv[1])
