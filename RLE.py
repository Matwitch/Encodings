

def RLE_encode(data: bytes,
               min_seq_len_to_compress: int = 3) -> bytes:
    
    N = len(data)
    encoded_data = bytearray()

    def write_same_byte(beg: int, end: int):
        if end - beg <= 0:
            return

        L = 128 + (end - beg)
        b = data[beg]

        encoded_data.append(L)
        encoded_data.append(b)

    def write_different_bytes(beg: int, end: int):
        if end - beg <= 0:
            return
        
        L = end - beg
        b = data[beg:end]

        encoded_data.append(L)
        encoded_data.extend(b)


    consecutive_count = 1
    i = 0
    prev_byte = data[0]
    for j in range(1, N):

        if consecutive_count == 127:
            write = True

        elif j - i == 127:
            write = True

        elif data[j] == prev_byte:
            write = False
            consecutive_count += 1

        elif (data[j] != prev_byte):
            if consecutive_count >= min_seq_len_to_compress:
                write = True
            else:
                write = False
                consecutive_count = 1


        if write is True:
            c = (consecutive_count >= min_seq_len_to_compress) * consecutive_count
            write_different_bytes(i, j-c)
            write_same_byte(j-c, j)

            consecutive_count = 1
            i = j
        
        prev_byte = data[j]

    c = (consecutive_count >= min_seq_len_to_compress) * consecutive_count
    write_different_bytes(i, N-c)
    write_same_byte(N-c, N)

    return bytes(encoded_data)



def RLE_decode(data: bytes) -> bytes:
    N = len(data)
    decoded_data = bytearray()

    i = 0
    while i < N:
        l = data[i]
        if l > 128:
            different = False
            l -= 128
        elif l < 128:
            different = True
        else:
            raise RuntimeError("Zero byte corresponding to sequence length")
        
        i += 1
        
        if different:
            if i + l - 1 >= N:
                raise RuntimeError("Byte sequence length exceeds file length")
            
            decoded_data.extend(data[i:i+l])
            i += l
        
        else:
            if i >= N:
                raise RuntimeError("Byte sequence length exceeds file length")
            
            decoded_data.extend(int.to_bytes(data[i]) * l)
            i += 1


    return bytes(decoded_data)