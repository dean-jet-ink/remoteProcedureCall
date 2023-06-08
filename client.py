from unix_stream_socket import UnixStreamClientSocket
from rpc import RPCClient
import utility

def main():
    filepath = utility.getFilepath()

    socket = UnixStreamClientSocket(filepath, 1024, 60)
    
    rpc = RPCClient(socket)

    print(f"result: {rpc.floor(3.6)}")
    print(f"result: {rpc.nroot(3, 8)}")
    print(f"result: {rpc.reverse('hello world')}")
    print(f"result: {rpc.valid_anagram('knee', 'keen')}")
    print(f"result: {rpc.sort(['banana', 'lemon', 'apple'])}")

if __name__ == "__main__":
    main()