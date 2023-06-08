from abc import ABC, abstractmethod
from unix_stream_socket import UnixStreamServerSocket, UnixStreamClientSocket
from typing import List, Type, TypeVar
import math
import json
import uuid

T = TypeVar('T')

class RPCBase(ABC):
    @abstractmethod
    def floor(self, x: float) -> int:
        pass

    @abstractmethod
    def nroot(self, n: int, x: int) -> int:
        pass

    @abstractmethod
    def reverse(self, s: str) -> str:
        pass

    @abstractmethod
    def valid_anagram(self, s1: str, s2: str) -> bool:
        pass

    @abstractmethod
    def sort(self, strArr: List[str]) -> List[str]:
        pass
    
    def _type_check(self, x: T, type: Type[T]):
        if not isinstance(x, type):
            raise TypeError(f"Argument must be instance of {T} but actual type is {type(x)}")

class RPCServer(RPCBase):
    def __init__(self, socket: UnixStreamServerSocket):
        self.__socket = socket
        self.__method_dict = {
            self.floor.__name__: self.floor,
            self.nroot.__name__: self.nroot,
            self.reverse.__name__: self.reverse,
            self.valid_anagram.__name__: self.valid_anagram,
            self.sort.__name__: self.sort
        }
        self.__arguments_number = {
            self.floor.__name__: 1,
            self.nroot.__name__: 2,
            self.reverse.__name__: 1,
            self.valid_anagram.__name__: 2,
            self.sort.__name__: 1
        }

    def floor(self, params: List[T]) -> int:
        x = params[0]

        if type(x) == int:
            return x
        self._type_check(x, float)

        return math.floor(x)

    def nroot(self, params: List[T]) -> int:
        n = params[0]
        x = params[1]

        self._type_check(n, int)
        self._type_check(x, int)

        return math.pow(x, 1/n)

    def reverse(self, params: List[T]) -> str:
        s = params[0]

        self._type_check(s, str)

        return s[::-1]

    def valid_anagram(self, params: List[T]) -> bool:
        s1 = params[0]
        s2 = params[1]

        self._type_check(s1, str)
        self._type_check(s2, str)

        if len(s1) != len(s2):
            return False

        return sorted(s1) == sorted(s2)

    def sort(self, params: List[T]) -> List[str]:
        strArr = params[0]

        self._type_check(strArr, list)
        for x in strArr:
            self._type_check(x, str)

        return sorted(strArr)
    
    def __create_response(self, result: T, id: int) -> str:
        response_json = {
            "result": result,
            "result_type": type(result).__name__,
            "id": id
        }

        return json.dumps(response_json)

    def __dispatch(self, message: str) -> str:
        message_json = json.loads(message)

        method = message_json["method"]
        params = message_json["params"]
        id = message_json["id"]

        if self.__arguments_number[method] != len(params):
            raise TypeError(f"The method '{method}' requires {self.__arguments_number[method]} arguments, but {len(params)} arguments were provided.")

        result = self.__method_dict[method](params)
        return self.__create_response(result, id)
    
    def communicate(self):
        self.__socket.communicate(self.__dispatch)

class RPCClient(RPCBase):
    def __init__(self, socket: UnixStreamClientSocket):
        self.__socket = socket

    def __create_message(self, method: str, params: List[T], param_types: List[str]) -> str:
        params = [x for x in params]
        param_types = [str(x) for x in param_types]

        message_json = {
            "method": method,
            "params": params,
            "param_types": param_types,
            "id": str(uuid.uuid4())
        }

        return json.dumps(message_json)
    
    def __communicate(self, method: str, params: List[T], param_types: List[str]) -> T:
        message: str = self.__create_message(method, params, param_types)

        response: str = self.__socket.communicate(message)

        message_json = json.loads(message)
        response_json = json.loads(response)
        if message_json["id"] != response_json["id"]:
            raise RuntimeError("Client ID and Server ID mismatch.")
        
        return response_json["result"]
    
    def floor(self, x: float) -> int:
        if type(x) == int:
            return x

        self._type_check(x, float)

        return self.__communicate(self.floor.__name__, [x], [type(x).__name__])

    def nroot(self, n: int, x: int) -> int:
        self._type_check(n, int)
        self._type_check(x, int)

        return self.__communicate(self.nroot.__name__, [n, x], [type[n], type(x).__name__])

    def reverse(self, s: str) -> str:
        self._type_check(s, str)

        return self.__communicate(self.reverse.__name__, [s], [type(s).__name__])

    def valid_anagram(self, s1: str, s2: str) -> bool:
        self._type_check(s1, str)
        self._type_check(s2, str)

        return self.__communicate(self.valid_anagram.__name__, [s1, s2], [type(s1).__name__, type(s2).__name__])

    def sort(self, strArr: List[str]) -> List[str]:
        self._type_check(strArr, list)
        for x in strArr:
            self._type_check(x, str)

        return self.__communicate(self.sort.__name__, [strArr], [type(strArr).__name__])