from helpers import WriteBitStream, ReadBitStream
import heapq


class HuffmanNode:
    @staticmethod
    def create_leaf(symbol: str, weight: int):
        if (symbol is None) or (weight is None):
            raise ValueError("Symbol and weight cannot be None")
        
        if weight < 0:
            raise ValueError("Weight cannot be negative")
        
        return HuffmanNode(None, None, symbol, weight)
    
    @staticmethod
    def create_internal(node0, node1):
        if (node0 is None) or (node1 is None):
            raise ValueError("Child nodes cannot be None")
        
        if not isinstance(node0, HuffmanNode) or not isinstance(node1, HuffmanNode):
            raise ValueError("Child nodes must be instances of HuffmanNode")
        
        return HuffmanNode(node0, node1, None, None)


    def __init__(self, node0, node1, symbol, weight):
        if (node0 is None) and (node1 is None) and (symbol is not None) and (weight is not None):
            self.symbol = symbol
            self.weight = weight
            self.node0 = None
            self.node1 = None

        elif (node0 is not None) and (node1 is not None) and isinstance(node0, HuffmanNode) and isinstance(node1, HuffmanNode) and (symbol is None) and (weight is None):
            self.symbol = None
            self.weight = node0.weight + node1.weight
            self.node0 = node0
            self.node1 = node1

        else:
            raise ValueError("Invalid parameters for HuffmanNode")
        
    def __lt__(self, other) -> bool:
        return self.weight < other.weight

    def is_leaf(self) -> bool:
        if (self.node0 is None) and (self.node1 is None) and (not (self.symbol is None)) and (not (self.weight is None)):
            return True
        elif (not (self.node0 is None)) and (not (self.node1 is None)) and (self.symbol is None) and (not (self.weight is None)):
            return False
        else:
            raise ValueError("Invalid HuffmanNode state")
        

    def get_code_dict(self, prefix: tuple) -> dict:
        if self.is_leaf():
            return {self.symbol: prefix}
        
        else:
            code_dict = {}
            code_dict.update(self.node0.get_code_dict(prefix + tuple([False])))
            code_dict.update(self.node1.get_code_dict(prefix + tuple([True])))

            return code_dict
        

def count_byte_frequencies(data: bytes) -> dict:
    frequency_dict = {}
    
    for b in range(0, 256):
        frequency_dict[b] = 0

    for byte in data:
        frequency_dict[byte] += 1
    
    return frequency_dict


def build_huffman_tree(frequency_dict: dict) -> HuffmanNode:
    if not frequency_dict:
        raise ValueError("Frequency dictionary cannot be empty")
    
    priority_queue = []
    
    for symbol, freq in frequency_dict.items():
        if freq < 0:
            raise ValueError("Frequency must be non-negative")
        leaf_node = HuffmanNode.create_leaf(symbol, freq)
        heapq.heappush(priority_queue, leaf_node)
    
    while len(priority_queue) > 1:
        node0 = heapq.heappop(priority_queue)
        node1 = heapq.heappop(priority_queue)
        
        internal_node = HuffmanNode.create_internal(node0, node1)
        heapq.heappush(priority_queue, internal_node)
    
    return priority_queue[0]


class HuffmanCodeIterator:
    def __init__(self, root: HuffmanNode):
        if not isinstance(root, HuffmanNode):
            raise ValueError("Root must be an instance of HuffmanNode")
        
        self.root = root
        self.current_node = root

    def read_bit(self, bit: bool):
        if self.current_node.is_leaf():
            raise ValueError("Cannot read bit from a leaf node")
        
        if bit:
            self.current_node = self.current_node.node1
        else:
            self.current_node = self.current_node.node0
        
        if self.current_node.is_leaf():
            symbol = self.current_node.symbol
            self.current_node = self.root
            return symbol
        else:
            return None
        


def huffman_encode(data: bytes) -> bytes:
    freq = count_byte_frequencies(data)
    h_tree = build_huffman_tree(freq)
    code_dict = h_tree.get_code_dict(tuple())

    ws = WriteBitStream()

    for b in range(0, 256):
        ws.write_byte(int.to_bytes(b, length=1, byteorder='big'))
        ws.write_bytes(int.to_bytes(freq.get(b, 0), length=4, byteorder='big'))


    ws.write_bytes(int.to_bytes(len(data), length=4, byteorder='big'))    

    for b in data:
        code = code_dict[b]
        ws.write_bits(code)

    
    return ws.get_data()


def huffman_decode(data: bytes) -> bytes:
    rs = ReadBitStream(data)

    freq = {}

    for _ in range(256):
        b = rs.read_byte()
        if b != _:
            raise ValueError("Incorrect Huffman frequency table format")
        
        f_bytes = rs.read_bytes(4)
        freq[b] = int.from_bytes(f_bytes, byteorder='big')

    N = int.from_bytes(rs.read_bytes(4), byteorder='big')

    h_tree = build_huffman_tree(freq)
    code = HuffmanCodeIterator(h_tree)

    B = bytearray()

    for _ in range(N):
        symbol = None
        while symbol is None:
            bit = rs.read_bit()
            symbol = code.read_bit(bit)
        
        B.append(symbol)
    
    return bytes(B)