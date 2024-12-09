import os
import tkinter as tk
from tkinter import filedialog, ttk
from pathlib import Path
import subprocess
import threading

class VideoConverter:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Format Converter")
        
        # Configure main window
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file = tk.StringVar()
        self.output_format = tk.StringVar(value="mp4")
        self.status = tk.StringVar(value="Ready")
        self.progress = tk.DoubleVar(value=0)
        
        self._create_widgets()
        
    def _create_widgets(self):
        # Input file section
        input_frame = ttk.LabelFrame(self.root, text="Input", padding="10")
        input_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(input_frame, textvariable=self.input_file, width=50).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Browse", command=self._browse_file).pack(side="right")
        
        # Output format section
        format_frame = ttk.LabelFrame(self.root, text="Output Format", padding="10")
        format_frame.pack(fill="x", padx=10, pady=5)
        
        formats = ["mp4", "mkv", "av1", "gif", "webp"]
        for fmt in formats:
            ttk.Radiobutton(format_frame, text=fmt, value=fmt, 
                           variable=self.output_format).pack(side="left", padx=10)
        
        # Convert button
        ttk.Button(self.root, text="Convert", command=self._start_conversion).pack(pady=10)
        
        # Progress section
        progress_frame = ttk.LabelFrame(self.root, text="Progress", padding="10")
        progress_frame.pack(fill="x", padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=300, mode='determinate',
                                          variable=self.progress)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(progress_frame, textvariable=self.status).pack()
        
    def _browse_file(self):
        filetypes = (
            ('Video files', '*.mp4;*.mkv;*.av1;*.gif;*.webp'),
            ('All files', '*.*')
        )
        
        filename = filedialog.askopenfilename(
            title='Select a video file',
            filetypes=filetypes
        )
        
        if filename:
            self.input_file.set(filename)
            
    def _convert_video(self):
        input_path = self.input_file.get()
        if not input_path:
            self.status.set("Please select an input file")
            return
        
        output_format = self.output_format.get()
        output_path = str(Path(input_path).with_suffix(f'.{output_format}'))
        
        try:
            self.status.set("Converting...")
            self.progress.set(0)
            
            # FFmpeg command construction
            command = ['ffmpeg', '-i', input_path]
            
            # Format-specific settings
            if output_format == 'gif':
                command.extend(['-vf', 'fps=10,scale=320:-1'])
            elif output_format == 'webp':
                command.extend(['-vf', 'fps=10,scale=320:-1', '-loop', '0'])
            elif output_format == 'av1':
                command.extend(['-c:v', 'libaom-av1', '-crf', '30', '-b:v', '0'])
            
            command.extend(['-y', output_path])
            
            # Execute conversion
            process = subprocess.Popen(
                command,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            # Monitor conversion progress
            duration = None
            for line in process.stderr:
                if "Duration" in line:
                    duration = self._parse_duration(line)
                elif "time=" in line and duration:
                    current_time = self._parse_time(line)
                    if current_time and duration:
                        progress = (current_time / duration) * 100
                        self.progress.set(progress)
                        self.root.update()
            
            process.wait()
            
            if process.returncode == 0:
                self.status.set("Conversion completed successfully!")
                self.progress.set(100)
            else:
                self.status.set("Conversion failed!")
                
        except Exception as e:
            self.status.set(f"Error: {str(e)}")
            
    def _start_conversion(self):
        # Run conversion in a separate thread to keep UI responsive
        thread = threading.Thread(target=self._convert_video)
        thread.daemon = True
        thread.start()
            
    def _parse_duration(self, line):
        try:
            time_str = line.split("Duration: ")[1].split(",")[0]
            h, m, s = map(float, time_str.split(":"))
            return h * 3600 + m * 60 + s
        except:
            return None
            
    def _parse_time(self, line):
        try:
            time_str = line.split("time=")[1].split()[0]
            h, m, s = map(float, time_str.split(":"))
            return h * 3600 + m * 60 + s
        except:
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoConverter(root)
    root.mainloop()