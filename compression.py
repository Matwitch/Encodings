from typing import Literal
from helpers import MTF, inverse_MTF, BWT, inverse_BWT
from RLE import RLE_encode, RLE_decode
from Huffman import huffman_encode, huffman_decode
from LZW import lzw_compress, lzw_decompress
from numpy import ceil
from copy import deepcopy

BWT_BLOCK_SIZE = 512
MTF_ALPH = [i for i in range(256)]

def compress(data: bytes, alg: Literal["RLE", "Huffman", "LZW"], **options) -> bytes:
    _options = deepcopy(options)
    for key in list(_options.keys()):
        if isinstance(_options[key], str):
            _options[key] = _options[key].lower()

        if isinstance(key, str):
            key_lower = key.lower()
            _options[key_lower] = _options.pop(key)
            
    if not ("bwt" in _options) and not ("mtf" in _options):
        _data = data
    else:
        _data = bytearray(data)

    if "bwt" in _options and _options["bwt"]:
        new_data = bytearray(b'BWT_')

        if len(_data) % BWT_BLOCK_SIZE != 0:
            padding_size = BWT_BLOCK_SIZE - (len(_data) % BWT_BLOCK_SIZE)
            new_data.extend(
                padding_size.to_bytes(int(ceil(BWT_BLOCK_SIZE.bit_length() / 8)), byteorder='big')
            )
            new_data.extend(b'_')
            _data.extend(b'\x00' * padding_size)

        for i in range(0, len(_data), BWT_BLOCK_SIZE):
            new_data.extend(BWT(_data[i:i+BWT_BLOCK_SIZE]))
        
        _data = new_data

    if "mtf" in _options and _options["mtf"]:
        _data = MTF(_data, MTF_ALPH)
        
        _data = bytearray(b'MTF_') + _data

    _data = bytes(_data)

    _alg = alg
    if isinstance(alg, str):
        _alg = alg.lower()

    if _alg == "rle":
        return bytes(b'RLE_') + RLE_encode(_data)
    elif _alg == "huffman":
        return bytes(b'HUFFMAN_') + huffman_encode(_data)
    elif _alg == "lzw":
        return bytes(b'LZW_') + lzw_compress(_data)
    else:
        raise ValueError("Unknown compression algorithm")
    



def decompress(data: bytes, alg: Literal["RLE", "Huffman", "LZW"] | None = None, **options) -> bytes:
    _options = deepcopy(options)
    for key in list(_options.keys()):
        if isinstance(_options[key], str):
            _options[key] = _options[key].lower()

        if isinstance(key, str):
            key_lower = key.lower()
            _options[key_lower] = _options.pop(key)
    
    _alg = alg
    if isinstance(alg, str):
        _alg = alg.lower()

    if (_alg == "rle") or data.startswith(b'RLE_'):
        if not data.startswith(b'RLE_'):
            raise ValueError("Data does not start with required RLE_ header")
        if (_alg is not None) and (_alg != "rle"):
            raise ValueError("Algorithm mismatch: data indicates RLE, but different algorithm specified")
        
        _data = RLE_decode(data[4:])

    elif (_alg == "huffman") or data.startswith(b'HUFFMAN_'):
        if not data.startswith(b'HUFFMAN_'):
            raise ValueError("Data does not start with required HUFFMAN_ header")
        if (_alg is not None) and (_alg != "huffman"):
            raise ValueError("Algorithm mismatch: data indicates Huffman, but different algorithm specified")
        
        _data = huffman_decode(data[8:])

    elif (_alg == "lzw") or data.startswith(b'LZW_'):
        if not data.startswith(b'LZW_'):
            raise ValueError("Data does not start with required LZW_ header")
        if (_alg is not None) and (_alg != "lzw"):
            raise ValueError("Algorithm mismatch: data indicates LZW, but different algorithm specified")

        _data = lzw_decompress(data[4:])
    
    else:
        raise ValueError("Unknown compression algorithm")


    if ("mtf" in _options and _options["mtf"]) or _data.startswith(b'MTF_'):
        if not _data.startswith(b'MTF_'):
            raise ValueError("Decoded data does not start with required MTF_ header")
        if ("mtf" in _options and not _options["mtf"]):
            raise ValueError("Data indicates MTF applied, but MTF parameter is False")
        
        _data = inverse_MTF(_data[4:], MTF_ALPH)
    
    bwt_padding_size = 0
    if ("bwt" in _options and _options["bwt"]) or _data.startswith(b'BWT_'):
        if not _data.startswith(b'BWT_'):
            raise ValueError("Decoded data does not start with required BWT_ header")
        if ("bwt" in _options and not _options["bwt"]):
            raise ValueError("Data indicates BWT applied, but BWT parameter is False")
        
        _data = _data[4:]

        idx_size = int(ceil(BWT_BLOCK_SIZE.bit_length() / 8))
        block_size = BWT_BLOCK_SIZE + idx_size

        if (int.from_bytes(_data[:idx_size], byteorder='big') < BWT_BLOCK_SIZE) and (_data[idx_size] == ord(b'_')):
            bwt_padding_size = int.from_bytes(_data[:idx_size], byteorder='big')
            _data = _data[idx_size+1:]

        if len(_data) % block_size != 0:
            raise ValueError("Data length is not a multiple of BWT block size")
        
        new_data = bytearray()

        for i in range(0, len(_data), block_size):
            new_data.extend(
                inverse_BWT(_data[i:i+block_size], idx_size)
            )

        _data = new_data

    return bytes(_data[:-bwt_padding_size] if bwt_padding_size > 0 else _data)