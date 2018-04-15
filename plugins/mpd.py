import socket
from .base import PluginBase


class MPDPlugin(PluginBase):

    def configure(self):
        defaults = {
            'format': '{song}',
            'port': 6600,
            'host': '127.0.0.1',
        }
        self.current_song = ''
        self.song_index = 0 
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
        s.recv(100)

        status = self.get_mpdstatus(s)
        if status['state'] != 'stop':

            s.send(b'currentsong\n')

            resp = "" 
            while "\nOK\n" not in resp:
                resp += s.recv(1).decode('ascii')
            s.close()

            song = resp.split('\n')[0].split('/')
            song = song[len(song)-1]
            song = song[0:-4]
            # add a space for clean wrapping
            song += ' | '
        else:
            song = '(stopped)'

        s.close()

        if song != '(stopped)':
            # scroll, for some reason
            if song != self.current_song:
                self.song_index = 0
                self.current_song = song

            song_text = song[self.song_index:][0:25]
            i = 0
            while(len(song_text) < 25 and i < len(song) - 1):
                song_text += song[i]
                i += 1

            self.song_index += 1
            if self.song_index >= len(song):
                self.song_index = 0
            # end scroll logic
        else:
            song_text = song

        song_info = {
            'song': '%s' % song_text
        }
        return song_info

    def update(self):
        locals().update(self.get_cursong())
        self.set_text(self.config['format'] % locals())
