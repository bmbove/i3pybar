"""
get_ip source:
http://stackoverflow.com/a/9267833
"""
import array
import fcntl
import socket
import struct

from .base import PluginBase

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
calls = {
    'SIOCGIFADDR': 0x8915,
    'SIOCGIWESSID': 0x8B1B,
}

class NetworkPlugin(PluginBase):

    def configure(self, config):
        if not config.get('cache_time', False):
            config['cache_time'] = 2.0
        if not config.get('format', False):
            config['format'] = '{essid} {ip}'
        config['format'] = self.fix_format(config['format'])
        return config

    def get_ip(self, iface):
        iface = iface.encode('utf-8')
        ifreq = struct.pack('16sH14s', iface, socket.AF_INET, b'\x00'*14)
        try:
            res = fcntl.ioctl(sockfd, calls['SIOCGIFADDR'], ifreq)
        except:
            return None
        ip = struct.unpack('16sH2x4s8x', res)[2]
        return socket.inet_ntoa(ip)

    def get_essid(self, interface):
        maxLength = {
            "interface": 16,
            "essid": 32
        }
        """Return the ESSID for an interface, or None if we aren't connected."""
        interface = interface.ljust(maxLength["interface"], "\0").encode('utf-8')
        essid = array.array("B", "\0".encode('utf-8') * maxLength["essid"])
        essidPointer, essidLength = essid.buffer_info()
        request = array.array("B",
            interface +           
            struct.pack("PHH",   
                essidPointer,   
                essidLength,   
                0)            
        )                    
        fcntl.ioctl(sock.fileno(), calls["SIOCGIWESSID"], request)
        name = essid.tostring().decode('utf-8').rstrip('\0')
        if name:
            return name
        return "-"

    def wifi_info(self):
        ifaces = {}
        info = self.read_file('/proc/net/wireless', start=2)
        for line in info.split("\n"):
            l_arr = [item for item in line.strip().split(" ") if item]
            if len(l_arr) > 0:
                ifaces[l_arr[0].replace(":", "")] = {
                    'status': l_arr[1],
                    'link': l_arr[2].replace(".", "%"),
                    'level': l_arr[3].replace(".", "dB"),
                    'noise': l_arr[4] + "dB",
                }
        self.wifi = ifaces

    def update(self):
        self.info = {
            'ip': '',
            'essid': '',
            'status': '',
            'link': '',
            'level': '',
            'noise': '',
        }

        self.wifi_info()

        if 'interface' not in self.config:
            for key in self.wifi.keys():
                self.config['interface'] = key
                break
            
        iface = self.config['interface']

        if iface in self.wifi:
            for key, value in self.wifi[iface].items():
                self.info[key] = value
            self.info['essid'] = self.get_essid(iface)

        self.info['ip'] = self.get_ip(iface)
        locals().update(self.info)
        self.set_text(self.config['format'] % locals())
