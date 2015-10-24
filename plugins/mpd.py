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

    def get_mpdstatus(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.config['host'], self.config['port']))
        s.send(b'currentsong\n')

        status = "" 
        while "\nOK\n" not in status:
            status += s.recv(1).decode('ascii')
        s.close()

        song = status.split('\n')[1].split('/')
        song = song[len(song)-1]
        song = song[0:-4]

        song_info = {
            'song': '%s' % song 
        }

        return song_info

    def update(self):
        locals().update(self.get_mpdstatus())
        self.set_text(self.config['format'] % locals())
