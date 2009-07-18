import appuifw
import pickle
import socket
import sys
import time

SERVICE_NAME = 'MPD BT Gateway'

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

    return s

def send_cmd(s, cmd):
    s.send(pickle.dumps(cmd))
    res = s.recv(1000)
    print res
    obj = pickle.loads(res)

    return obj

def list_to_unicode(obj):
    list = []
    for item in obj:
        list.append(unicode(item))

    return list

s = connect()

try:
    cmd = ('pause', 0)
    obj = send_cmd(s, cmd)

    cmd = ('list', 'Artist')
    obj = send_cmd(s, cmd)
    print obj
    list = list_to_unicode(obj)
    #idx = appuifw.popup_menu(list)
    #print idx

    #cmd = ('currentsong',)
    #obj = send_cmd(s, cmd)
    #print obj['title']
    #appuifw.app.title = unicode(obj['title'])
    #
    #cmd = ('list', 'Album', 'Artist', 'AC/DC')
    #obj = send_cmd(s, cmd)
    #list = list_to_unicode(obj)
    #if len(list) > 0:
    #    appuifw.popup_menu(list)

    cmd = ('play',)
    send_cmd(s, cmd)
finally:
    s.close()

