# file: simple_uwp_gui_with_row_buttons.py
import os

from compression import compress, decompress
from helpers import read_bin_file_data, write_bin_data_to_file

import tkinter as tk
from tkinter import filedialog, ttk



# ------------------ Callbacks ------------------
def select_file():
    path = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("All files", "*.*")]
    )
    if path:
        filepath.delete(0, tk.END)
        filepath.insert(0, path)



def on_decode():
    if not os.path.exists(filepath.get()):
        log_textbox.config(text="Such file does not exist", foreground="red")
        return
    
    name = os.path.splitext(filepath.get())[0]
    ext = os.path.splitext(filepath.get())[1]
    dir = os.path.dirname(filepath.get())

    data = read_bin_file_data(filepath.get())

    log_textbox.config(text="Decoding...", foreground="blue")
    root.update_idletasks()
    
    try:
        decoded_data = decompress(
            data,
            alg=algorithm.get(),
            bwt=bwt_flag.get(),
            mtf=mtf_flag.get()
        )
    
    except RuntimeError as e:
        log_textbox.config(text=f"DECODING ERROR: {e} \nMake sure that file is {algorithm.get()}-encoded.", foreground="red")
        root.config(cursor="")
        return
    except ValueError as e:
        log_textbox.config(text=f"ERROR: {e} \nMake sure that decoding options correspond to the file encoding.", foreground="red")
        root.config(cursor="")
        return

    root.config(cursor="")

    save_filepath = filedialog.asksaveasfilename(
        title="Save File",
        initialdir=dir,
        defaultextension="*.*",            # Default file extension
        filetypes=[("All files", "*.*")]   # Filter file types
    )
    
    if save_filepath: 
        write_bin_data_to_file(decoded_data, save_filepath)
        log_textbox.config(text=f"Decoding: \n{filepath.get()} \nAlgorithm: \n{algorithm.get()} \n with parameters: BWT={bwt_flag.get()}, MTF={mtf_flag.get()}", foreground="blue")
    
    else:
        log_textbox.config(text="Saving cancelled", foreground="red")


        

def on_encode():
    if not os.path.exists(filepath.get()):
        log_textbox.config(text="Such file does not exist", foreground="red")
        return
    
    name = os.path.splitext(os.path.basename(filepath.get()))[0]
    ext = os.path.splitext(filepath.get())[1]
    dir = os.path.dirname(filepath.get())

    data = read_bin_file_data(filepath.get())
    log_textbox.config(text="Encoding...", foreground="blue")
    root.update_idletasks()

    try:
        encoded_data = compress(
            data,
            alg=algorithm.get(),
            bwt=bwt_flag.get(),
            mtf=mtf_flag.get()
        )
    
    except RuntimeError as e:
        log_textbox.config(text=f"ENCODING ERROR: {e} \nSorry", foreground="red")
        return
    except ValueError as e:
        log_textbox.config(text=f"ERROR: {e} \nSorry", foreground="red")
        return


    save_filepath = filedialog.asksaveasfilename(
        title="Save File",
        initialdir=dir,
        initialfile=name + f"_{algorithm.get()}_encoded.bin",
        defaultextension=".bin",            # Default file extension
        filetypes=[("Binary files", "*.bin"),
                    ("All files", "*.*")]   # Filter file types
    )
    
    if save_filepath: 
        write_bin_data_to_file(encoded_data, save_filepath)
        log_textbox.config(text=f"Encoding: \n{filepath.get()} \nAlgorithm: \n{algorithm.get()} \nwith parameters: BWT={bwt_flag.get()}, MTF={mtf_flag.get()}", foreground="blue")
    
    else:
        log_textbox.config(text="Saving cancelled", foreground="red")





# ------------------ GUI ------------------
root = tk.Tk()
root.title("Encode/Decode File")
root.geometry("480x540")
root.configure(bg="#ffffff")

style = ttk.Style()
style.theme_use('clam')
style.configure('Colored.TFrame', background='#ffffff')




# ===== CHOOSE FILE =====
ttk.Button(root, text="Choose File...", command=select_file).pack(pady=(25, 7))

filepath = ttk.Entry(root, width=70)
filepath.pack()
# ===== CHOOSE FILE =====


# ===== SELECT ALGORITHM =====
ttk.Label(root, text="Select Algorithm:", background="#ffffff").pack(pady=(25, 7))
algorithm = ttk.Combobox(root, width=30, state="readonly")
algorithm['values'] = ("RLE", "Huffman", "LZW")
algorithm.current(0)
algorithm.pack()
# ===== SELECT ALGORITHM =====


# ===== OPTIONAL PARAMETERS =====
ttk.Label(root, text="Parameters:", background="#ffffff").pack(pady=(25, 7))

options_frame = ttk.Frame(root, style='Colored.TFrame')
options_frame.pack(pady=(25, 7))

bwt_flag = tk.BooleanVar(value=False)
mtf_flag = tk.BooleanVar(value=False)

bwt = tk.Checkbutton(options_frame, text="Burrows-Wheeler", variable=bwt_flag, background="#ffffff")
mtf = tk.Checkbutton(options_frame, text="Move To Front", variable=mtf_flag, background="#ffffff")
bwt.grid(row=0, column=0, padx=15, pady=5, sticky="w")
mtf.grid(row=1, column=0, padx=15, pady=5, sticky="w")


# ===== OPTIONAL PARAMETERS =====



# ===== ENCODE/DECODE BUTTONS =====
button_frame = ttk.Frame(root, style='Colored.TFrame')
button_frame.pack(pady=(25, 7))

ttk.Button(button_frame, text="Encode", command=on_encode).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="Decode", command=on_decode).grid(row=0, column=1, padx=10)
# ===== ENCODE/DECODE BUTTONS =====



# ===== LOG TEXTBOX =====
# progress = ttk.Progressbar(root, mode="indeterminate", length=300)
# progress.pack(pady=25)
log_textbox = ttk.Label(root, text="", foreground="blue", background="#ffffff")
log_textbox.pack(pady=25)
# ===== LOG TEXTBOX =====



# Center window
root.eval('tk::PlaceWindow . center')
root.mainloop()