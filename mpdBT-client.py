import appuifw
import e32
import pickle
import socket
import sys
import time

SERVICE_NAME = 'MPD BT Gateway'
s = None
loop = True

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

    #print 'Connected'

    return s

def send_cmd(cmd):
    s = get_socket()

    msg = pickle.dumps(cmd)
    try:
        s.send(str(len(msg)))
        s.send(msg)
        size = int(s.recv(1024))
        data = ''
        while (len(data) < size):
            data = data + s.recv(1024)
        obj = pickle.loads(data)
    except:
        disconnect()
        return None

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
    cmd = ('list', 'Artist')
    obj = send_cmd(cmd)
    list = list_to_unicode(obj)
    list.sort()
    idx = selection_list(list)
    if idx is None:
        return None
    artist = list[idx]
    set_title(artist)

    cmd = ('list', 'Album', 'Artist', artist.encode('utf-8'))
    obj = send_cmd(cmd)
    list = list_to_unicode(obj)
    list.sort()
    if len(list) > 0:
        idx = selection_list(list)
        if idx is None:
            return None
        album = list[idx]
        set_title(album)

        cmd = ('find', 'Album', album.encode('utf-8'))
        obj = send_cmd(cmd)
        tracks = []
        for track in obj:
            if 'track' in track and 'title' in track and 'artist' in track and track['artist'] == artist.encode('utf-8'):
                tracks.append(track)

        tracks.sort(lambda x, y: cmp(int(x['track']), int(y['track'])))
        list = []
        for track in tracks:
            list.append(unicode(track['title'].decode('utf-8')))
        if len(list) > 0:
            idx = selection_list(list)
            if idx is None:
                return None
            track = tracks[idx]

            return track
        else:
            #print 'No tracks'
            pass

    return None

def popup_menu(list):
    return appuifw.popup_menu(list)

def selection_list(list):
    return appuifw.selection_list(list, 1)

def enqueue_song(path):
    obj = send_cmd(('add', path))
    update_playlist()

def select_and_enqueue_song():
    track = select_song()
    if track:
        enqueue_song(track['file'])

def pause_song():
    obj = send_cmd(('pause', 1))

def play_song(id=None):
    send_cmd(('play',))

def previous_song():
    send_cmd(('previous',))

def next_song():
    send_cmd(('next',))

def show_playlist():
    obj = send_cmd(('playlistinfo',))
    list = []
    for track in obj:
        list.append(unicode(track['title'].decode('utf-8')))
    if len(list) > 0:
        appuifw.popup_menu(list)
    else:
        appuifw.note(u'Empty')

def clear_playlist():
    send_cmd(('clear',))
    update_playlist()

def get_current_song():
    obj = send_cmd(('currentsong',))
    return obj['title']

def quit():
    disconnect()
    appuifw.app.set_exit()

def disconnect():
    global s
    #print 'Disconnect'
    if s:
        s.close()

    s = None

def set_title(title):
    if title.__class__.__name__ != 'unicode':
        title = unicode(title.decode('utf-8'))
    appuifw.app.title = title

def item_selected():
    idx = appuifw.app.body.current()
    send_cmd(('play', idx))

def get_current():
    obj = send_cmd(('status',))
    idx, state = ('0', 'Unknown')
    if 'song' in obj:
        idx = obj['song']
    if 'state' in obj:
        state = obj['state']

    return (int(idx), state)

def update_playlist(move = False):
    obj = send_cmd(('playlistinfo',))
    if obj is None:
        return
    list = []
    current, state = get_current()
    for track in obj:
        pos = int(track['pos'])
        if pos == current:
            list.append((unicode(track['title'].decode('utf-8')), unicode(track['artist'].decode('utf-8')) + u' [' + unicode(state) + u']'))
        else:
            list.append((unicode(track['title'].decode('utf-8')), unicode(track['artist'].decode('utf-8'))))

    if len(list) == 0:
            appuifw.app.body.set_list(['...'], idx)
    else: 
        if move:
            idx = current
        else:
            idx = appuifw.app.body.current()
        if len(list) < idx:
            idx = 0
        appuifw.app.body.set_list(list, idx)

try:
    appuifw.app.menu = [
            (u'Playlist', (
                (u'Show', show_playlist),
                (u'Clear', clear_playlist),
                (u'Enqueue', select_and_enqueue_song),
                )),
            (u'Playback', (
                (u'Play', play_song),
                (u'Pause', pause_song),
                (u'Previous', previous_song),
                (u'Next', next_song),
                )),
            (u'Disconnect', disconnect),
            ]

    appuifw.exit_key_handler = quit

    appuifw.app.body = appuifw.Listbox([(u'', u'')])

    while loop:
        update_playlist(True)
        e32.ao_sleep(10)
finally:
    disconnect()
