from socket_base import SocketBase
import socket
import os
import sys
from typing import Callable
from threading import Thread

class UnixStreamServerSocket(SocketBase):
    def __init__(self, address: str, recv_buffer_size: int = 1024):
        super().__init__(socket.AF_UNIX, socket.SOCK_STREAM, recv_buffer_size)
        self.__address = address

    def __bind(self):
        if os.path.exists(self.__address):
            os.unlink(self.__address)

        print(f"Starting up on {self.__address}")
        self._socket.bind(self.__address)

    def __recv_data(self, connection: socket.socket, callback: Callable[[str], str]) -> str:
        try:
            byte_parts = b''

            while True:
                part = connection.recv(self._recv_buffer_size)
                byte_parts += part

                if byte_parts.find(b'END') != -1:
                    break

            message = byte_parts.decode("utf-8")
            message = message.replace("END", "")
            response = callback(message)
            print(f"reseponse: {response}")
            self.__send_data(connection, response)
            
        except ConnectionResetError as e:
            print(e)
        except BrokenPipeError as e:
            print(e)
        finally:
            connection.close()

    def __send_data(self, connection: socket.socket, response: str):
        response += "END"
        connection.sendall(response.encode("utf-8"))
    
    def communicate(self, callback: Callable[[str], str]):
        self._create_socket()

        self.__bind()

        self._socket.listen(5)

        while True:
            connection, _ = self._socket.accept()

            thread = Thread(target = self.__recv_data, args = (connection, callback))
            thread.start()


class UnixStreamClientSocket(SocketBase):
    def __init__(self, server_address: str, recv_buffer_size: int = 1024, timeout: int = 60):
        super().__init__(socket.AF_UNIX, socket.SOCK_STREAM, recv_buffer_size)
        self.__server_address = server_address
        self.__timeout = timeout

    def __connect(self):
        try:
            self._socket.connect(self.__server_address)
        except socket.error as e:
            print(e)
            sys.exit(1)

    def __recv_data(self) -> str:
        try:
            self._socket.settimeout(self.__timeout)

            byte_parts = b''

            while True:
                part = self._socket.recv(self._recv_buffer_size)
                byte_parts += part

                if byte_parts.find(b'END') != -1:
                    break
            
            response = byte_parts.decode("utf-8")
            response = response.replace("END", "")
            print(response)
            return response

        except ConnectionResetError as e:
            raise Exception(e)
        except BrokenPipeError as e:
            raise Exception(e)
        except TimeoutError as e:
            raise Exception(e)
        finally:
            self._close()
    
    def __send_data(self, message: str):
        message += "END"
        self._socket.sendall(message.encode("utf-8"))

    def communicate(self, message: str) -> str:
        self._create_socket()
        print(f"Connecting to {self.__server_address}")
        self.__connect()
        self.__send_data(message)

        return self.__recv_data()

        