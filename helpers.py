import os
import copy

class ReadBitStream:
    def __init__(self, data: bytes | bytearray):
        if isinstance(data, bytes):
            self.data = data
        elif isinstance(data, bytearray):
            self.data = copy.deepcopy(data)
        else:
            raise ValueError(f"Unsupported data type: {type(data)}")
        
        self.i = 0
        self.j = 0
        self.N = len(data) * 8

        self._masks = bytes([1, 2, 4, 8, 16, 32, 64, 128])

        self.eos = False

        pass


    def _next(self, k: int = 1):
        self.j += ((self.i + k) // 8)
        self.i = (self.i + k) % 8
        
        if self.i + 8*self.j >= self.N:
            self.eos = True


    def read_bit(self):
        if self.eos:
            raise RuntimeError("EOS")
        
        b = bool(self.data[self.j] & self._masks[self.i])
        self._next()
        
        return b

    def read_byte(self):
        if self.eos or (self.i + 8*self.j + 8 > self.N):
            raise RuntimeError("EOS")
        
        first = (self.data[self.j] >> self.i)
        second = (self.data[self.j] << (8 - self.i))

        self._next(8)
        
        return (first | second)
    

    def read_bits(self, k):
        B = [False] * k

        for l in range(k):
            B[l] = self.read_bit()
        
        return B

    def read_bytes(self, k):
        B = bytes(k)

        for l in range(k):
            B[l] = self.read_byte()
        
        return B
    
    

class WriteBitStream:
    def __init__(self):
        self.data = bytearray()
        
        self.i = 0
    
        self._masks = bytes([1, 2, 4, 8, 16, 32, 64, 128])

        pass


    def _next(self, k: int = 1):
        self.j += ((self.i + k) // 8)
        self.i = (self.i + k) % 8
        
        if self.i + 8*self.j >= self.N:
            self.eos = True


    def read_bit(self):
        if self.eos:
            raise RuntimeError("EOS")
        
        b = bool(self.data[self.j] & self._masks[self.i])
        self._next()
        
        return b

    def read_byte(self):
        if self.eos or (self.i + 8*self.j + 8 > self.N):
            raise RuntimeError("EOS")
        
        first = (self.data[self.j] >> self.i)
        second = (self.data[self.j] << (8 - self.i))

        self._next(8)
        
        return (first | second)


def read_bin_file_data(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        data = f.read()

    return data


def write_bin_data_to_file(data, filepath: str) -> bytes:
    path, ext = os.path.splitext(filepath)

    with open(filepath, 'wb') as f: 
        f.write(data)
