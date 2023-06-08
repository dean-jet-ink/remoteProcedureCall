from unix_stream_socket import UnixStreamServerSocket
from rpc import RPCServer
import utility

def main():
    filepath = utility.getFilepath()

    socket = UnixStreamServerSocket(filepath, 8)

    rpc = RPCServer(socket)

    rpc.communicate()

if __name__ == "__main__":
    main()