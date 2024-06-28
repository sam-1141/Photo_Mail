import re
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import importlib
from PIL import Image, ImageTk
import os
import sys
import json
import requests  # Add this import to check internet connection

# Add the scripts directory to the system path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR)
sys.path.append(SCRIPTS_DIR)

import settings_variables as sv  # Import the settings variables
from Core_Functions import capture_and_send_email

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller stores temporary files in _MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class MyApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo_Mail")
        
        # Load settings from config file
        self.load_settings()

        # Get screen width and height
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Set window size to fit the screen
        self.root.geometry(f"{self.screen_width}x{self.screen_height}")
        self.root.resizable(True, True)  # Allow window resizing

        # Initialize dictionaries to hold references to UI elements
        self.entries = {}
        self.selected_frame = tk.StringVar(value=sv.MY_Frame if hasattr(sv, 'MY_Frame') else sv.MY_FRAME_01)
        self.frame_images = {}

        # Create context menu
        self.create_context_menu()

        # Create a canvas to enable scrolling pyinstaller 
        # --name main --onefile --windowed --icon=icon.ico main.py 
        #pyinstaller main.spec


        self.create_scrollable_canvas()

        # Play introductory video
        self.play_intro_video()

    def create_context_menu(self):
        # Create a context menu with a Refresh option
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Refresh", command=self.refresh)

        # Bind right-click event to show the context menu
        self.root.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        # Display the context menu at the cursor position
        self.context_menu.post(event.x_root, event.y_root)

    def create_scrollable_canvas(self):
        # Create a frame to hold the canvas and scrollbar
        self.canvas_frame = ttk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        # Create a canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg='black')  # Set canvas background color
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Create a vertical scrollbar linked to the canvas
        self.scrollbar = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to use the scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Create a frame inside the canvas to hold the content
        self.content_frame = ttk.Frame(self.canvas, style='Content.TFrame')
        self.canvas.create_window((self.screen_width//2, 0), window=self.content_frame, anchor=tk.N, width=self.screen_width)

        # Bind mouse wheel events to the canvas
        self.content_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind_all("<MouseWheel>", self.on_mouse_wheel)

        # Define custom style for content frame
        style = ttk.Style()
        style.configure('Content.TFrame', background='#FF6F00')

    def on_frame_configure(self, event):
        # Update the scroll region to match the size of the content frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_mouse_wheel(self, event):
        # Scroll the canvas using the mouse wheel
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def refresh(self):
        # Save the current selected frame
        current_frame = self.selected_frame.get()
        
        # Remove all existing widgets
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        # Reinitialize the application without the video intro
        self.entries = {}
        self.create_context_menu()
        self.create_tabs()

        # Restore the selected frame
        self.selected_frame.set(current_frame)

    def play_intro_video(self):
        intro_video_path = sv.INTRO_VIDEO  # Replace with your actual path to video file
        
        # Open the video file
        cap = cv2.VideoCapture(intro_video_path)

        if not cap.isOpened():
            print("Error: Could not open video file.")
            self.create_tabs()  # Proceed to create tabs without video if failed to open

        else:
            # Create a label to hold video frames
            intro_label = tk.Label(self.content_frame)
            intro_label.pack(fill=tk.BOTH, expand=True)

            # Function to update video frames
            def update_frame():
                ret, frame = cap.read()

                # Convert frame from OpenCV BGR format to RGB
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                    # Resize frame to fit label size
                    resized_frame = cv2.resize(frame_rgb, (self.screen_width, self.screen_height))

                    # Convert frame to ImageTk format
                    img = Image.fromarray(resized_frame)
                    img_tk = ImageTk.PhotoImage(image=img)

                    # Update label with new frame
                    intro_label.configure(image=img_tk)
                    intro_label.image = img_tk

                    # Call update_frame function after 30 milliseconds
                    intro_label.after(30, update_frame)
                else:
                    # End of video, close the video capture
                    cap.release()
                    self.remove_intro_video_and_create_tabs(intro_label)

            # Start updating frames
            update_frame()

    def remove_intro_video_and_create_tabs(self, intro_label):
        # Remove the intro video label
        intro_label.pack_forget()

        # Create tabs
        self.create_tabs()

    def create_tabs(self):
        tab_control = ttk.Notebook(self.content_frame)
        style = ttk.Style()
        
        # Define a new style for the Notebook Tab
        style.configure('TNotebook.Tab', font=('Consolas', 20, 'bold'), foreground='green')

        # Tab 1 - Main
        tab1 = ttk.Frame(tab_control)
        tab_control.add(tab1, text='Main Tab 📋')
        self.create_main_tab_content(tab1)

        # Tab 2 - Settings
        tab2 = ttk.Frame(tab_control)
        tab_control.add(tab2, text='Settings Tab ⚙️')
        self.create_settings_tab_content(tab2)

        # Tab 3 - About
        tab3 = ttk.Frame(tab_control)
        tab_control.add(tab3, text='About Tab ℹ️')
        self.create_about_tab_content(tab3)

        tab_control.pack(expand=1, fill='both')
        
        # Bind the tab change event to reload settings
        tab_control.bind("<<NotebookTabChanged>>", self.on_tab_change)

    def on_tab_change(self, event):
        # Reload settings when switching back to the Main tab
        selected_tab = event.widget.tab(event.widget.select(), "text")
        if (selected_tab == "Main Tab 📋"):
            self.reload_settings()
            self.update_main_tab_ui()

    def reload_settings(self):
        # Reload the settings from settings_variables.py
        print("Reloading settings...")
        importlib.reload(sv)
        print(f"Settings reloaded: {sv.__dict__}")

    def update_main_tab_ui(self):
        # Update the main tab UI with the new settings values if needed
        self.load_frame_images()

    def create_main_tab_content(self, tab):
        style = ttk.Style()
        style.configure('TLabel', 
                background='black', 
                foreground='orange', 
                font=('Arial', 14), 
                padding=10)

        # Configure TButton with more modern look
        style.configure('TButton', 
                background='orange', 
                foreground='black', 
                font=('Arial', 12, 'bold'), 
                padding=10, 
                relief='flat')

        # Additional styling for hover effect on TButton
        style.map('TButton', 
          background=[('active', '#FFA500')],  # lighter orange on hover
          foreground=[('active', 'black')])
        
        # Add widgets and functionality for the Main tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)
        tab.grid_columnconfigure(2, weight=1)

        # Add the internet status label
        self.internet_status_label = tk.Label(tab, text="", font=("Arial", 24))
        self.internet_status_label.grid(row=0, column=2, pady=10, padx=20, sticky='ne')

        # Email entry box
        email_icon_label = ttk.Label(tab, text="📧", font=('bold', 24), background="#C0C0C0",foreground= 'black')
        email_icon_label.grid(row=0, column=1, pady=5)

        email_label = ttk.Label(tab, text="Please Enter Your e-mail:", style='TLabel')
        email_label.grid(row=1, column=1, pady=10)
        self.email_entry = tk.Text(tab, width=33, height=1.2, font=('Arial', 20), bg='#C0C0C0')
        self.email_entry.grid(row=2, column=1)
        self.email_entry.bind("<KeyRelease>", self.update_email_color)
        self.email_entry.bind("<Return>", self.capture_and_send_photo)  # Bind Enter key to the button click

        # Frame selection radio buttons and thumbnails
        frame_01_radio = ttk.Radiobutton(tab, text="Use Frame 01", variable=self.selected_frame, value="MY_FRAME_01", command=self.update_frame_selection)
        frame_01_radio.grid(row=3, column=1, pady=5)
        self.frame_01_image_label = ttk.Label(tab)
        self.frame_01_image_label.grid(row=4, column=1, pady=5)
        self.frame_01_image_label.bind("<Button-1>", lambda event: self.select_frame("MY_FRAME_01"))

        frame_02_radio = ttk.Radiobutton(tab, text="Use Frame 02", variable=self.selected_frame, value="MY_FRAME_02", command=self.update_frame_selection)
        frame_02_radio.grid(row=5, column=1, pady=5)
        self.frame_02_image_label = ttk.Label(tab)
        self.frame_02_image_label.grid(row=6, column=1, pady=5)
        self.frame_02_image_label.bind("<Button-1>", lambda event: self.select_frame("MY_FRAME_02"))

        # Load initial frame images
        self.load_frame_images()

        # Capture and send photo button
        capture_button = ttk.Button(tab, text="Capture and Send photo", style='TButton', command=self.capture_and_send_photo)
        capture_button.grid(row=7, column=1, pady=20)

        style.configure("Green.TLabel", background="green", foreground="white", font=('Arial', 14, 'italic'), borderwidth=2, relief="solid")
        style.configure("Red.TLabel", background="red", foreground="white", font=('Arial', 14, 'italic'), borderwidth=2, relief="solid")

        instruction_label_green = ttk.Label(tab, text="Press SPACE bar to capture", style="Green.TLabel")
        instruction_label_green.grid(row=8, column=1, pady=10, padx=20, sticky=tk.W)

        camera_label = ttk.Label(tab, text="📷", font=('Arial', 24), background="#C0C0C0", foreground="black")
        camera_label.grid(row=8, column=1, pady=10, padx=20, sticky=tk.E)

        instruction_label_red = ttk.Label(tab, text="Press ESC to cancel", style="Red.TLabel")
        instruction_label_red.grid(row=9, column=1, pady=10, padx=20, sticky=tk.W)

        cancel_label = ttk.Label(tab, text="❌", font=('Arial', 24), background="#C0C0C0", foreground="red")
        cancel_label.grid(row=9, column=1, pady=10, padx=20, sticky=tk.E)

        # Update internet status
        self.update_internet_status()

    def update_email_color(self, event):
        email_text = self.email_entry.get("1.0", tk.END).strip()
        self.email_entry.delete("1.0", tk.END)

        at_index = email_text.find("@")
        if (at_index != -1):
            before_at = email_text[:at_index]
            after_at = email_text[at_index:]
            self.email_entry.insert(tk.END, before_at, "before_at")
            self.email_entry.insert(tk.END, after_at, "after_at")
            self.email_entry.tag_configure("before_at", foreground="blue")
            self.email_entry.tag_configure("after_at", foreground= '#36454F')
        else:
            self.email_entry.insert(tk.END, email_text)
            self.email_entry.tag_remove("before_at", "1.0", tk.END)
            self.email_entry.tag_remove("after_at", "1.0", tk.END)

    def validate_email(self, email):
        regex = r'^\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.match(regex, email)

    def capture_and_send_photo(self, event=None):
        receiver_email = self.email_entry.get("1.0", tk.END).strip()
        if receiver_email and self.validate_email(receiver_email):
            capture_and_send_email(receiver_email, self.root, self)  # Pass the MyApplication instance
        else:
            messagebox.showwarning("Input Error", "Please enter a valid email address.")

    def load_frame_images(self):
        self.load_image('MY_FRAME_01', self.frame_01_image_label)
        self.load_image('MY_FRAME_02', self.frame_02_image_label)

    def load_image(self, frame_key, label):
        frame_path = getattr(sv, frame_key)
        try:
            img = Image.open(frame_path)
            img.thumbnail((img.width // 10, img.height // 10))
            img_tk = ImageTk.PhotoImage(img)
            label.configure(image=img_tk)
            label.image = img_tk
        except Exception as e:
            label.configure(text="No Image")

    def select_frame(self, frame_key):
        self.selected_frame.set(frame_key)
        self.update_frame_selection()

    def update_frame_selection(self):
        selected_frame_key = self.selected_frame.get()
        frame_path = getattr(sv, selected_frame_key)
        sv.MY_Frame = frame_path  # Update the session variable
        self.update_config('MY_Frame', frame_path)  # Update the config file
        self.save_settings()

    def create_settings_tab_content(self, tab):
        # Add widgets and functionality for the Settings tab
        style = ttk.Style()
        style.configure('TLabel', background='black', foreground='orange', font=('Arial', 14))
        style.configure('TButton', background='orange', foreground='black', font=('Arial', 12, 'bold'))

        # Centering the settings tab content
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)
        tab.grid_columnconfigure(2, weight=1)

        # Create entry boxes for each setting variable
        settings = [
            ('Sender Email', 'SENDER_EMAIL'),
            ('Sender Password', 'SENDER_PASSWORD'),
            ('Frame Image 01', 'MY_FRAME_01'),
            ('Frame Image 02', 'MY_FRAME_02'),
            ('Webcam Width', 'WEBCAM_WIDTH'),
            ('Webcam Height', 'WEBCAM_HEIGHT'),
            ('Email Subject', 'MESSAGE_SUBJECT'),
            ('Email Body', 'MESSAGE_BODY'),
            ('Intro Video', 'INTRO_VIDEO')
        ]

        for i, setting in enumerate(settings):
            label = ttk.Label(tab, text=f"{setting[0]}:", style='TLabel')
            label.grid(row=i*2, column=1, pady=5, sticky=tk.W)
            entry_options = {'width': 50, 'font': ('Arial', 12)}
            if setting[1] == 'SENDER_PASSWORD':
                entry_options['show'] = '*'
            entry = ttk.Entry(tab, **entry_options)
            entry.grid(row=i*2+1, column=1, pady=5)
            entry.insert(0, getattr(sv, setting[1]))
            self.entries[setting[1]] = entry

        # Buttons to choose the frame images and intro video
        choose_frame_01_button = ttk.Button(tab, text="Choose Frame 01 🗂️➕", style='TButton', command=self.choose_frame_01_image)
        choose_frame_01_button.grid(row=len(settings)*2, column=1, pady=5)

        choose_frame_02_button = ttk.Button(tab, text="Choose Frame 02 🗂️➕", style='TButton', command=self.choose_frame_02_image)
        choose_frame_02_button.grid(row=len(settings)*2+1, column=1, pady=5)

        choose_video_button = ttk.Button(tab, text="Choose Intro Video 🎞️", style='TButton', command=self.choose_intro_video)
        choose_video_button.grid(row=len(settings)*2+2, column=1, pady=5)

        # Save settings button
        save_button = ttk.Button(tab, text="Save Settings 💾", style='TButton', command=self.save_settings)
        save_button.grid(row=len(settings)*2+3, column=1, pady=20)

    def choose_frame_01_image(self):
        # Open a file dialog to choose the frame image
        file_path = filedialog.askopenfilename(
            title="Choose Frame 01 Image 🗂️➕",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.entries['MY_FRAME_01'].delete(0, tk.END)
            self.entries['MY_FRAME_01'].insert(0, file_path)
            self.update_config('MY_FRAME_01', file_path)
            self.load_image('MY_FRAME_01', self.frame_01_image_label)

    def choose_frame_02_image(self):
        # Open a file dialog to choose the frame image
        file_path = filedialog.askopenfilename(
            title="Choose Frame 02 Image 🗂️➕",
            filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif"), ("All files", "*.*")]
        )
        if file_path:
            self.entries['MY_FRAME_02'].delete(0, tk.END)
            self.entries['MY_FRAME_02'].insert(0, file_path)
            self.update_config('MY_FRAME_02', file_path)
            self.load_image('MY_FRAME_02', self.frame_02_image_label)

    def choose_intro_video(self):
        # Open a file dialog to choose the intro video
        file_path = filedialog.askopenfilename(
            title="Choose Intro Video 🎞️",
            filetypes=[("Video files", "*.mp4 *.avi *.mov *.mkv"), ("All files", "*.*")]
        )
        if file_path:
            self.entries['INTRO_VIDEO'].delete(0, tk.END)
            self.entries['INTRO_VIDEO'].insert(0, file_path)
            self.update_config('INTRO_VIDEO', file_path)

    def save_settings(self):
        try:
            # Update the settings_variables.py file with new values
            config_path = resource_path('config.json')
            with open(config_path, 'r+') as f:
                config = json.load(f)
                for key, entry in self.entries.items():
                    value = entry.get()
                    if key in ['WEBCAM_WIDTH', 'WEBCAM_HEIGHT']:
                        config[key] = int(value)
                    else:
                        config[key] = value
                f.seek(0)
                f.write(json.dumps(config, indent=4))
                f.truncate()

            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
            self.reload_settings()
            self.update_settings_tab_ui()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {str(e)}")

    def update_config(self, key, value):
        config_path = resource_path('config.json')
        with open(config_path, 'r+') as f:
            config = json.load(f)
            config[key] = value
            f.seek(0)
            f.write(json.dumps(config, indent=4))
            f.truncate()

    def update_settings_tab_ui(self):
        # Update the settings tab UI with the new settings values
        for key, entry in self.entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, getattr(sv, key))

    def create_about_tab_content(self, tab):
        # Add widgets and functionality for the About tab
        tab.grid_columnconfigure(0, weight=1)
        tab.grid_columnconfigure(1, weight=3)
        tab.grid_columnconfigure(2, weight=1)

        label = ttk.Label(tab, text="About Tab Content")
        label.grid(row=0, column=1, padx=20, pady=20)

    def load_settings(self):
        config_path = resource_path('config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            for key, value in config.items():
                setattr(sv, key, value)

    def update_internet_status(self):
        try:
            # Try to connect to a website to check the internet connection
            requests.get("https://www.google.com", timeout=5)
            self.internet_status_label.configure(text="📶", fg="green")  # Wi-Fi available emoji
        except requests.ConnectionError:
            self.internet_status_label.configure(text="🚫", fg="red")  # No Wi-Fi emoji
        
        # Check the internet status every 10 seconds
        self.root.after(10000, self.update_internet_status)

if __name__ == "__main__":
    root = tk.Tk()
    app = MyApplication(root)
    root.mainloop()
