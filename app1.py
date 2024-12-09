import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import TkinterDnD, DND_FILES
import ffmpeg
import os
import subprocess
import threading

# Function to perform video conversion
def convert_video(input_file, output_format, bitrate=None, fps=None):
    file_name, _ = os.path.splitext(input_file)
    output_file = f"{file_name}.{output_format}"
    
    try:
        stream = ffmpeg.input(input_file)
        if bitrate:
            stream = stream.output(output_file, video_bitrate=bitrate)
        else:
            stream = stream.output(output_file)
        
        if fps:
            stream = stream.filter('fps', fps=fps)

        stream.run()
        return output_file
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error during conversion: {e}")

# Function to handle file selection
def select_files():
    file_paths = filedialog.askopenfilenames(filetypes=[("Video Files", "*.mp4 *.mkv *.av1")])
    if file_paths:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, ", ".join(file_paths))

# Function to start the conversion process with progress
def start_conversion():
    file_paths = input_entry.get().split(", ")
    output_format = format_var.get().lower()
    bitrate = bitrate_slider.get()
    fps = fps_slider.get()

    if not file_paths:
        messagebox.showerror("Error", "Please select input files.")
        return

    if not output_format:
        messagebox.showerror("Error", "Please select an output format.")
        return

    progress_bar.start()
    convert_button.config(state=tk.DISABLED)
    open_button.config(state=tk.DISABLED)
    
    def run_conversion():
        for input_file in file_paths:
            try:
                output_path = convert_video(input_file, output_format, bitrate, fps)
                messagebox.showinfo("Success", f"File converted successfully: {output_path}")
                open_button.output_path = output_path  # Save path for Open button
                open_button.config(state=tk.NORMAL)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        progress_bar.stop()
        convert_button.config(state=tk.NORMAL)
    
    threading.Thread(target=run_conversion).start()

# Function to open the converted file
def open_converted_file():
    output_path = open_button.output_path
    if output_path:
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':  # macOS or Linux
            subprocess.call(('xdg-open', output_path))

# Function to handle drag-and-drop of files
def on_drop(event):
    files = event.data.split()
    input_entry.delete(0, tk.END)
    input_entry.insert(0, ", ".join(files))

# Set up the main window with TkinterDnD
root = TkinterDnD.Tk()
root.title("Video Converter")
root.geometry("400x400")

# Input file selection
input_label = tk.Label(root, text="Select Video File(s):")
input_label.pack(pady=5)

input_entry = tk.Entry(root, width=40)
input_entry.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=select_files)
browse_button.pack(pady=5)

# Enable drag-and-drop for input files
root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', on_drop)

# Output format selection
format_label = tk.Label(root, text="Select Output Format:")
format_label.pack(pady=5)

format_var = tk.StringVar()
format_choices = ["MP4", "MKV", "AV1", "GIF", "WEBP"]
format_menu = tk.OptionMenu(root, format_var, *format_choices)
format_menu.pack(pady=5)

# Bitrate slider
bitrate_label = tk.Label(root, text="Select Bitrate (kbps):")
bitrate_label.pack(pady=5)

bitrate_slider = tk.Scale(root, from_=500, to=8000, orient="horizontal")
bitrate_slider.set(2000)  # Default bitrate
bitrate_slider.pack(pady=5)

# Frame rate slider
fps_label = tk.Label(root, text="Select Frame Rate (fps):")
fps_label.pack(pady=5)

fps_slider = tk.Scale(root, from_=5, to=60, orient="horizontal")
fps_slider.set(30)  # Default frame rate
fps_slider.pack(pady=5)

# Convert button
convert_button = tk.Button(root, text="Convert", command=start_conversion)
convert_button.pack(pady=10)

# Progress bar
progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="indeterminate")
progress_bar.pack(pady=5)

# Open file button (initially disabled)
open_button = tk.Button(root, text="Open Converted File", state=tk.DISABLED, command=open_converted_file)
open_button.pack(pady=10)

# Run the GUI loop
root.mainloop()
