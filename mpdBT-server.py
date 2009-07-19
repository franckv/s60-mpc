import bluetooth
import mpd
import pickle
import sys

SERVICE_NAME = 'MPD BT Gateway'
MPD_HOST = 'localhost'
MPD_PORT = '6600'

def make_socket():
    s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    s.bind(("", bluetooth.PORT_ANY))
    s.listen(1)

    bluetooth.advertise_service(s, SERVICE_NAME, '', service_classes=[bluetooth.SERIAL_PORT_CLASS], profiles=[bluetooth.SERIAL_PORT_PROFILE])

    return s

def handle_cmd(cmd, args):
    print "received [%s] with [%s]" % (cmd, str(args))

    try:
        status = client.status()
    except:
        print 'Reconnecting'
        client.disconnect()
        client.connect(MPD_HOST, MPD_PORT)
        status = client.status()
        
    if not status:
        print 'Connection closed'
        sys.exit(1)

    try:
        if args:
            result = getattr(client, cmd)(*args)
        else:
            result = getattr(client, cmd)()
    except:
        result = 'Invalid command'

    return result

def handle_client():
    c, addr = s.accept()
    print "Accepted connection from ",addr

    while (True):
        try:
            size = int(c.recv(1024))
            data = ''
            while (len(data) < size):
                data = data + c.recv(1024)
        except:
            break

        data = pickle.loads(data)
        cmd = data[0]
        if len(cmd) > 1:
            args = data[1:]
        else:
            args = None

        if cmd == 'exit':
            s.close()
            sys.exit(0)
        
        result = handle_cmd(cmd, args)
        msg = pickle.dumps(result)
        c.send(str(len(msg)))
        c.send(msg)

    c.close()

client = mpd.MPDClient()
client.connect(MPD_HOST, MPD_PORT)

status = client.status()
if not status:
    print 'Connection closed'
    sys.exit(1)

s = make_socket()
while (True):
    handle_client()
s.close()
