import socket
from .base import PluginBase


class MPDPlugin(PluginBase):

    def configure(self):
        defaults = {
            'format': '{song}',
            'port': 6600,
            'host': '0',
        }
        return defaults

    def get_mpdstatus(self, s):
        s.send(b'status\n')
        status = "" 
        while "\nOK\n" not in status:
            status += s.recv(1).decode('ascii')

        status = status.split('\n')
        status_d = {}
        for line in status:
            if ':' in line:
                l = line.split(':')
                status_d[l[0]] = l[1].strip()

        return status_d

    def get_cursong(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.config['host'], self.config['port']))

        status = self.get_mpdstatus(s)
        if status['state'] != 'stop':

            s.send(b'currentsong\n')

            status = "" 
            while "\nOK\n" not in status:
                status += s.recv(1).decode('ascii')
            s.close()

            song = status.split('\n')[1].split('/')
            song = song[len(song)-1]
            song = song[0:-4]
        else:
            song = '(stopped)'

        s.close()

        song_info = {
            'song': '%s' % song 
        }

        return song_info

    def update(self):
        locals().update(self.get_cursong())
        self.set_text(self.config['format'] % locals())
