import appuifw
import pickle
import socket
import sys
import time

SERVICE_NAME = 'MPD BT Gateway'
s = None

def connect():
    dev = socket.bt_discover()
    if dev and  SERVICE_NAME in dev[1]:
        host = dev[0]
        port = dev[1][SERVICE_NAME]
    else:
        appuifw.note(u'Service not found')
        sys.exit(1)

    s = socket.socket(socket.AF_BT, socket.SOCK_STREAM)
    s.connect((host, port))

    print 'Connected'

    return s

def send_cmd(s, cmd):
    msg = pickle.dumps(cmd)
    s.send(str(len(msg)))
    s.send(msg)
    size = int(s.recv(1024))
    data = ''
    while (len(data) < size):
        data = data + s.recv(1024)
    obj = pickle.loads(data)

    return obj

def list_to_unicode(obj):
    list = []
    for item in obj:
        list.append(unicode(item.decode('utf-8')))

    return list

def get_socket():
    global s
    if s is None:
        s = connect()
    return s

def select_song():
    s = get_socket()

    cmd = ('list', 'Artist')
    obj = send_cmd(s, cmd)
    list = list_to_unicode(obj)
    list.sort()
    idx = popup_menu(list)
    artist = list[idx]
    set_title(artist)

    cmd = ('list', 'Album', 'Artist', artist.encode('utf-8'))
    obj = send_cmd(s, cmd)
    list = list_to_unicode(obj)
    list.sort()
    if len(list) > 0:
        idx = popup_menu(list)
        album = list[idx]
        set_title(album)

        cmd = ('find', 'Album', album.encode('utf-8'))
        obj = send_cmd(s, cmd)
        tracks = []
        for track in obj:
            if 'track' in track and 'title' in track and 'artist' in track and track['artist'] == artist.encode('utf-8'):
                tracks.append(track)

        tracks.sort(lambda x, y: cmp(int(x['track']), int(y['track'])))
        list = []
        for track in tracks:
            list.append(unicode(track['title'].decode('utf-8')))
        if len(list) > 0:
            idx = popup_menu(list)
            track = tracks[idx]

            return track
        else:
            print 'No tracks'

    return None

def popup_menu(list):
    return appuifw.popup_menu(list)

def enqueue_song(path):
    s = get_socket()

    cmd = ('add', path)
    obj = send_cmd(s, cmd)

def select_and_enqueue_song():
    track = select_song()
    enqueue_song(track['file'])

def pause_song():
    s = get_socket()

    cmd = ('pause', 1)
    obj = send_cmd(s, cmd)

def play_song(id=None):
    s = get_socket()

    cmd = ('play',)
    send_cmd(s, cmd)

def previous_song():
    pass

def next_song():
    pass

def disconnect():
    global s
    if s:
        s.close()

    s = None

def set_title(title):
    if title.__class__.__name__ != 'unicode':
        title = unicode(title.decode('utf-8'))
    appuifw.app.title = title

try:
    appuifw.app.menu = [
            (u'Pause', pause_song),
            (u'Play', play_song),
            (u'Enqueue', select_and_enqueue_song),
            (u'Previous', previous_song),
            (u'Next', next_song),
            (u'Disconnect', disconnect),
            (u'Quit', disconnect),
            ]

    #s = get_socket()
    #cmd = ('currentsong',)
    #obj = send_cmd(s, cmd)
    #set_title(obj['title'])

finally:
    if s:
        s.close()

