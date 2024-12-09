import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import ffmpeg
import os
import subprocess

# Function to perform video conversion
def convert_video(input_file, output_format):
    file_name, _ = os.path.splitext(input_file)
    output_file = f"{file_name}.{output_format}"
    
    try:
        # Run ffmpeg command and update the progress bar
        ffmpeg.input(input_file).output(output_file).run()
        return output_file
    except ffmpeg.Error as e:
        raise RuntimeError(f"Error during conversion: {e}")

# Function to handle file selection
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.mkv *.av1")])
    if file_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, file_path)

# Function to start the conversion process with progress
def start_conversion():
    input_file = input_entry.get()
    output_format = format_var.get().lower()

    if not input_file:
        messagebox.showerror("Error", "Please select an input file.")
        return

    if not output_format:
        messagebox.showerror("Error", "Please select an output format.")
        return

    try:
        # Update the progress bar to indicate conversion start
        progress_bar.start()
        output_path = convert_video(input_file, output_format)
        progress_bar.stop()
        messagebox.showinfo("Success", f"File converted successfully: {output_path}")
        
        # Enable the open button and save the output path
        open_button.config(state=tk.NORMAL)
        open_button.output_path = output_path

    except Exception as e:
        progress_bar.stop()
        messagebox.showerror("Error", str(e))

# Function to open the converted file
def open_converted_file():
    output_path = open_button.output_path
    if output_path:
        if os.name == 'nt':  # Windows
            os.startfile(output_path)
        elif os.name == 'posix':  # macOS or Linux
            subprocess.call(('xdg-open', output_path))

# Set up the main window
root = tk.Tk()
root.title("Video Converter")
root.geometry("400x250")

# Input file selection
input_label = tk.Label(root, text="Select Video File:")
input_label.pack(pady=5)

input_entry = tk.Entry(root, width=40)
input_entry.pack(pady=5)

browse_button = tk.Button(root, text="Browse", command=select_file)
browse_button.pack(pady=5)

# Output format selection
format_label = tk.Label(root, text="Select Output Format:")
format_label.pack(pady=5)

format_var = tk.StringVar()
format_choices = ["MP4", "MKV", "AV1", "GIF", "WEBP"]
format_menu = tk.OptionMenu(root, format_var, *format_choices)
format_menu.pack(pady=5)

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
