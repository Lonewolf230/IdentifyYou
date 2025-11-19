import tkinter as tk
from tkinter import ttk, filedialog,messagebox
import subprocess
import sys
import threading
import time

def choose_folder(target_var):
    folder = filedialog.askdirectory()
    if folder:
        target_var.set(folder)


root = tk.Tk()
root.title("Identify You")
root.geometry("900x750")
root.configure(bg="#f4f4f4")

def start_process():
    global proc
    source=src_var.get()
    dest=dest_var.get()
    ref=ref_var.get()
    print("Source:", source, "Dest:", dest, "Ref:", ref)
    if not source or not ref:
        messagebox.showerror("Error", "Please provide all folder paths.")
        return
    if not dest:
        dest="/".join(source.split("/")[:-1])+"/output"+time.strftime("_%Y%m%d-%H%M%S")
        dest_var.set(dest)
        print("Modified dest:", dest)
    print(sys.executable)
    proc=subprocess.Popen([
        sys.executable, 
        "main.py",
        "--source", source,
        "--dest", dest,
        "--ref", ref,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1)
    print("Process started")
    threading.Thread(target=read_output, daemon=True).start()
    log_box.insert("end", "Process started...\n")


def read_output():
    for line in proc.stdout:
        log_box.insert("end", line)
        log_box.see("end")

    log_box.insert("end", "\n=== Process Completed ===\n")
    log_box.see("end")
    log_box.insert("end",f"Output copied in folder : {dest_var.get()}\n")

style = ttk.Style()
style.configure("TLabel", background="#f4f4f4", font=("Arial", 14))
style.configure("Header.TLabel", font=("Arial", 36, "bold"), background="#f4f4f4")
style.configure("Sub.TLabel", font=("Arial", 16), background="#f4f4f4", wraplength=800)
style.configure("TButton", font=("Arial", 14), padding=8)

header = ttk.Label(root, text="Identify You", style="Header.TLabel")
header.pack(pady=10)

sub = ttk.Label(
    root,
    text=(
        "Drag and drop or browse a folder containing images, then provide "
        "reference images and a destination folder. The app will identify you "
        "using face recognition and copy matching images to the output folder."
    ),
    style="Sub.TLabel"
)
sub.pack(pady=5)

container = ttk.Frame(root, padding=20)
container.pack(pady=10)

src_var = tk.StringVar()
ref_var = tk.StringVar()
dest_var = tk.StringVar()

def folder_input(label_text, variable):
    box = ttk.Frame(container)
    
    lbl = ttk.Label(box, text=label_text, width=25, anchor="w")
    lbl.grid(row=0, column=0, padx=5, pady=8)

    entry = ttk.Entry(box, textvariable=variable, width=50)
    entry.grid(row=0, column=1, padx=5)

    btn = ttk.Button(box, text="Browse", command=lambda: choose_folder(variable))
    btn.grid(row=0, column=2, padx=5)

    box.pack(fill="x", pady=5)

folder_input("Source Image Folder:", src_var)
folder_input("Reference Images Folder:", ref_var)
folder_input("Destination Folder:", dest_var)

label_note = ttk.Label(
    root,
    text="Note: If destination folder is left empty, an output folder will be created next to the source folder.",
    style="Sub.TLabel"
) 
label_note.pack(pady=10)

start_btn = ttk.Button(root, text="Start Process", command=start_process)
start_btn.pack(pady=10)

log_box = tk.Text(root, width=100, height=20)
log_box.pack(pady=10)

root.mainloop()
