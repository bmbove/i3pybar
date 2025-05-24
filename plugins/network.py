"""
get_ip source:
http://stackoverflow.com/a/9267833

get_essid modified from:
http://stackoverflow.com/a/14142016
"""
import array
import fcntl
import socket
import struct
import time

from .base import PluginBase

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd = sock.fileno()
calls = {
    'SIOCGIFADDR': 0x8915,
    'SIOCGIWESSID': 0x8B1B,
}

class NetworkPlugin(PluginBase):

    def configure(self):
        defaults = {
            'interface': 'eth0',
            'cache_time': '2',
            'format': '{essid} {ip}'
        }
        self.last_data = { 'rx': 0, 'tx': 0}
        self.last_time = time.time()
        return defaults 

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
        name = essid.tobytes().decode('utf-8').rstrip('\0')
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

    def data_info(self):
        info = self.read_file('/proc/net/dev', start=2).strip()
        for line in info.split('\n'):
            data = [item for item in line.split(' ') if item]
            if(data[0][:-1] == self.iface):
                iface_data = {
                    'rx': int(data[1]),
                    'tx': int(data[9])
                }

                try:
                    d_rx = iface_data['rx'] - self.last_data['rx']
                    d_tx = iface_data['tx'] - self.last_data['tx']
                    iface_data['rx_speed'] = d_rx/(time.time() - self.last_time)
                    iface_data['tx_speed'] = d_tx/(time.time() - self.last_time)
                    self.last_data['rx'] = iface_data['rx']
                    self.last_data['tx'] = iface_data['tx']
                    self.last_time = time.time()
                except:
                    iface_data['rx_speed'] = 0
                    iface_data['tx_speed'] = 0
                    

        return iface_data


    def update(self):
        self.info = {
            'ip': '',
            'essid': '',
            'status': '',
            'link': '',
            'level': '',
            'noise': '',
            'total_up': '',
            'total_down': '',
            'tx_speed': '',
            'rx_speed': ''
        }

        self.wifi_info()

        if 'interface' not in self.config:
            for key in self.wifi.keys():
                self.config['interface'] = key
                break
            
        self.iface = self.config['interface']

        if self.iface in self.wifi:
            for key, value in self.wifi[self.iface].items():
                self.info[key] = value
            self.info['essid'] = self.get_essid(self.iface)

        usage = self.data_info()
        self.info['total_up'] = '{:7s}'.format(self.format_size(usage['tx']))
        self.info['total_down'] = '{:7s}'.format(self.format_size(usage['rx']))
        self.info['up_speed'] = '{:7s}/s'.format(
            self.format_size(usage['tx_speed'])
        )
        self.info['down_speed'] = '{:7s}/s'.format(
            self.format_size(usage['rx_speed'])
        )

        self.info['ip'] = self.get_ip(self.iface)

        fvars = self.info
        self.set_text(
            self.format_from_dict(self.config['format'], fvars)
        )
