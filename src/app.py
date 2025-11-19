import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from main import run_work 

root = tk.Tk()
root.title("Identify You")
root.geometry("900x750")
root.configure(bg="#f4f4f4")

style = ttk.Style()
style.configure("TLabel", background="#f4f4f4", font=("Arial", 12))
style.configure("Header.TLabel", font=("Arial", 28, "bold"), background="#f4f4f4")
style.configure("Sub.TLabel", font=("Arial", 12), background="#f4f4f4", wraplength=800)
style.configure("TButton", font=("Arial", 12), padding=6)

header = ttk.Label(root, text="Identify You", style="Header.TLabel")
header.pack(pady=10)

sub = ttk.Label(root, text="Select a source folder with images, a folder containing reference images, and a destination folder. The app will copy matching images to the destination.", style="Sub.TLabel")
sub.pack(pady=5)

container = ttk.Frame(root, padding=12)
container.pack(pady=10, fill="x")

src_var = tk.StringVar()
ref_var = tk.StringVar()
dest_var = tk.StringVar()

def choose_folder(target_var):
    folder = filedialog.askdirectory()
    if folder:
        target_var.set(folder)

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
folder_input("Destination Folder (optional):", dest_var)

note = ttk.Label(root, text="If destination is empty, an output folder will be created next to the source.", style="Sub.TLabel")
note.pack(pady=8)

start_btn = ttk.Button(root, text="Start Process")
start_btn.pack(pady=6)

log_box = tk.Text(root, width=100, height=20)
log_box.pack(pady=10)

def gui_log(msg):
    def append():
        log_box.insert("end", msg + "\n")
        log_box.see("end")
    root.after(0, append)

def start_process():
    source = src_var.get().strip()
    ref = ref_var.get().strip()
    dest = dest_var.get().strip()

    if not source or not ref:
        messagebox.showerror("Error", "Please provide both Source and Reference folders.")
        return

    if not dest:
        dest = os.path.join(os.path.dirname(source), "output" + time.strftime("_%Y%m%d-%H%M%S"))
        dest_var.set(dest)

    start_btn.config(state="disabled")
    log_box.insert("end", f"Starting: source={source} ref={ref} dest={dest}\n")
    log_box.see("end")

    def worker():
        try:
            result = run_work(source, dest, ref, log_callback=gui_log, max_workers=8)
            if result.get("success"):
                gui_log(f"Finished: matched {result['matched']}/{result['total']}. Output: {result['dest']}")
            else:
                gui_log(f"Failed: {result.get('reason', 'unknown')}")
        except Exception as e:
            gui_log(f"Exception in worker: {e}")
        finally:
            root.after(0, lambda: start_btn.config(state="normal"))

    threading.Thread(target=worker, daemon=True).start()

start_btn.config(command=start_process)

if __name__ == "__main__":
    root.mainloop()
