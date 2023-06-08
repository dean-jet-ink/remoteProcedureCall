from abc import ABC
import socket

class SocketBase(ABC):
    def __init__(self, family: int, typ: int, recv_buffer_size: int):
        self._socket = None
        self.__family = family
        self.__typ = typ
        self._recv_buffer_size = recv_buffer_size

    def _create_socket(self):
        self._socket = socket.socket(self.__family, self.__typ)

    def __del__(self):
        self._close()

    def _close(self):
        try:
            print("Closing socket")
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except:
            pass