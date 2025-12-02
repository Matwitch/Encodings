from helpers import WriteBitStream, ReadBitStream, int_to_bits, bits_to_int

MAX_DICT_SIZE = 2 ** 16

class IRWayTrie:
    class IRWayTrieNode:
        def __init__(self, index: int):
            self.children = {}
            self.index = index


        def add_child(self, char, index):
            if char in self.children:
                raise ValueError("Child already exists")
            
            self.children[char] = IRWayTrie.IRWayTrieNode(index)


    def __init__(self):
        self.root = self.IRWayTrieNode(None)
        self.root.children = {i: IRWayTrie.IRWayTrieNode(i) for i in range(256)}
        self.n_phrases = 256

        self.current_node = self.root

    def next(self, char: int):
        if not (0 <= char <= 255):
            raise ValueError("Character must be a byte")
        
        if char in self.current_node.children:
            self.current_node = self.current_node.children[char]
            
            return None
        
        else:
            if self.n_phrases < MAX_DICT_SIZE - 1:
                self.current_node.add_child(char, self.n_phrases)
                self.n_phrases += 1
            idx = self.current_node.index
            self.current_node = self.root.children[char]
            
            return idx


class IDict:
    def __init__(self):
        self.phrases = [bytes([i]) for i in range(256)]
        self.prev_phrase = None

    def next(self, index: int):
        if index < len(self.phrases):
            phrase = self.phrases[index]

        elif index == len(self.phrases):
            phrase = self.prev_phrase + bytes([self.prev_phrase[0]])
        
        else:
            raise ValueError("Invalid index")
        
        if not (self.prev_phrase is None) and (len(self.phrases) < MAX_DICT_SIZE-1):
            self.phrases.append(self.prev_phrase + bytes([phrase[0]]))
        
        self.prev_phrase = phrase
        return phrase
    


def lzw_compress(data: bytes) -> bytes:
    trie = IRWayTrie()
    output = WriteBitStream()

    index_bit_length = (trie.n_phrases - 1).bit_length()

    for byte in data:
        res = trie.next(byte)
        index_bit_length = (trie.n_phrases - 2).bit_length()

        if not (res is None):
            # print(f"Writing index ({index_bit_length}-bit):  {res}")
            output.write_bits(
                int_to_bits(res, index_bit_length)
            )

    
    if trie.current_node.index is not None:
        output.write_bits(
                int_to_bits(trie.current_node.index, index_bit_length)
            )

    return output.get_data()



def lzw_decompress(data: bytes) -> bytes:
    input = ReadBitStream(data)
    output = WriteBitStream()

    idict = IDict()
    index_bit_length = (len(idict.phrases) - 1).bit_length()

    while not (input.remaining_bits() < index_bit_length):
        index = bits_to_int(input.read_bits(index_bit_length))
        # print(f"Reading index ({index_bit_length}-bit):  {index}")
        phrase = idict.next(index)
        index_bit_length = (len(idict.phrases)).bit_length()
        # print(f"Writing phrase:  {phrase}")
        output.write_bytes(phrase)

    

    last = input.read_all_bits()
    if (len(last) > 0) and (bits_to_int(last) != 0):
        raise RuntimeError("Unable to decode the end of the stream")

    return output.get_data()