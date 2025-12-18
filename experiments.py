import os
import time
from helpers import read_bin_file_data
from compression import compress, decompress
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

data_table = pd.DataFrame(columns=["Algorithm", "File Type", "MTF", "BWT",
                             "Compression Ratio mean", "Compression Ratio std", "Encoding Speed mean", "Encoding Speed std"])

directory = "Test Files"
for alg in ["LZW"]:
    for ext in ["txt", "pdf", "png", "jpg", "mp3", "exe"]:
        for mtf in [True, False]:
            for bwt in [True, False]:
                compression_ratio = []
                encoding_speed = []
                for filename in os.listdir(f"{directory}/{ext}"):
                    filepath = f"{directory}/{ext}/{filename}"
                    if os.path.isfile(filepath):
                        data = read_bin_file_data(filepath)

                        og_len = len(data)
                        es_time = time.time()
                        encoded_data = compress(
                            data,
                            alg=alg,
                            bwt=bwt,
                            mtf=mtf
                        )
                        encoding_speed.append(
                            1024*(time.time() - es_time) / og_len
                        ) 
                        
                        enc_len = len(encoded_data)
                        decoded_data = decompress(encoded_data)
     
                        if (data == decoded_data):
                            print(enc_len / og_len)
                        else:
                            print(f"Error in file: {filepath}")

                        compression_ratio.append(enc_len / og_len)
                
                row_entry = {
                    "Algorithm": [alg],
                    "File Type": [ext],
                    "MTF": [mtf],
                    "BWT": [bwt],
                    "Compression Ratio mean": [np.mean(compression_ratio)],
                    "Compression Ratio std": [np.std(compression_ratio)],
                    "Encoding Speed mean": [np.mean(encoding_speed)],
                    "Encoding Speed std": [np.std(encoding_speed)],
                }

                data_table = pd.concat([data_table, pd.DataFrame.from_dict(row_entry)], ignore_index=True)
                data_table.to_csv("compression_results2.csv", index=False) 