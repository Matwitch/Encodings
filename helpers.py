import os


def read_bin_file_data(filepath: str) -> bytes:
    with open(filepath, "rb") as f:
        data = f.read()

    return data


def write_bin_data_to_file(data, filepath: str) -> bytes:
    path, ext = os.path.splitext(filepath)

    with open(filepath, 'wb') as f: 
        f.write(data)
