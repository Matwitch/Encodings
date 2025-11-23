# file: simple_uwp_gui_with_row_buttons.py
import os

from RLE import RLE_decode, RLE_encode
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

    if algorithm.get() == "RLE":
        try:
            decoded_data = RLE_decode(data)
        except RuntimeError as e:
            log_textbox.config(text=f"DECODING ERROR: {e} \nMake sure that file is {algorithm.get()}-encoded.", foreground="red")
            return


    else:
        log_textbox.config(text=f"Algorithm ({algorithm.get()}) is not supported yet", foreground="red")
        return


    save_filepath = filedialog.asksaveasfilename(
        title="Save File",
        initialdir=dir,
        defaultextension="*.*",            # Default file extension
        filetypes=[("All files", "*.*")]   # Filter file types
    )
    
    if save_filepath: 
        write_bin_data_to_file(decoded_data, save_filepath)
        log_textbox.config(text=f"Decoding: \n{filepath.get()} \nAlgorithm: \n{algorithm.get()} \nwith parameters: \n{parameters.get('1.0')}")
    
    else:
        log_textbox.config(text="Saving cancelled", foreground="red")


        

def on_encode():
    if not os.path.exists(filepath.get()):
        log_textbox.config(text="Such file does not exist", foreground="red")
        return
    
    name = os.path.basename(filepath.get())
    ext = os.path.splitext(filepath.get())[1]
    dir = os.path.dirname(filepath.get())

    data = read_bin_file_data(filepath.get())

    if algorithm.get() == "RLE":
        encoded_data = RLE_encode(data)
        

    else:
        log_textbox.config(text=f"Algorithm ({algorithm.get()}) is not supported yet", foreground="red")
        return


    save_filepath = filedialog.asksaveasfilename(
        title="Save File",
        initialdir=dir,
        initialfile=name + "_RLE_encoded.bin",
        defaultextension=".bin",            # Default file extension
        filetypes=[("Binary files", "*.bin"),
                    ("All files", "*.*")]   # Filter file types
    )
    
    if save_filepath: 
        write_bin_data_to_file(encoded_data, save_filepath)
        log_textbox.config(text=f"Encoding: \n{filepath.get()} \nAlgorithm: \n{algorithm.get()} \nwith parameters: \n{parameters.get('1.0')}")
    
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
algorithm['values'] = ("RLE", "Base64", "Huffman", "LZW")
algorithm.current(0)
algorithm.pack()
# ===== SELECT ALGORITHM =====


# ===== OPTIONAL PARAMETERS =====
ttk.Label(root, text="Parameters (Optional):", background="#ffffff").pack(pady=(25, 7))
parameters = tk.Text(root, height=4, wrap='word', relief='solid', bd=1)
parameters.pack(padx=25, fill='both', expand=False)
# ===== OPTIONAL PARAMETERS =====



# ===== ENCODE/DECODE BUTTONS =====
button_frame = ttk.Frame(root, style='Colored.TFrame')
button_frame.pack(pady=(25, 7))

ttk.Button(button_frame, text="Encode", command=on_encode).grid(row=0, column=0, padx=10)
ttk.Button(button_frame, text="Decode", command=on_decode).grid(row=0, column=1, padx=10)
# ===== ENCODE/DECODE BUTTONS =====



# ===== LOG TEXTBOX =====
log_textbox = ttk.Label(root, text="", foreground="blue")
log_textbox.pack(pady=25)
# ===== LOG TEXTBOX =====



# Center window
root.eval('tk::PlaceWindow . center')
root.mainloop()