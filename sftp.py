import socket
import paramiko

import config


class SFTP:

    def __init__(self, ip: str) -> None:
        self._ip = ip
        self._transport = paramiko.Transport((ip, config.hosts[ip]['port']))
        self._transport.set_keepalive(config.keepalive)
        self._transport.connect(username=config.hosts[ip]['username'], password=config.hosts[ip]['password'])
        self._sftp = self._transport.open_sftp_client()

    def file_exists(self, path: str) -> bool:
        try:
            self._sftp.stat(path)
            return True
        except IOError:
            return False

    def read_file(self, path: str) -> str:
        return self._sftp.open(path, mode='r').read().decode('utf_8')

    @property
    def hostname(self) -> str:
        return socket.getfqdn(self._ip)

    def is_active(self) -> bool:
        return self._transport.is_active()

    def close(self) -> None:
        self._transport.close()
