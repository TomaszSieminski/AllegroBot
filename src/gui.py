import tkinter as tk
from tkinterdnd2 import DND_FILES
from tkinter import messagebox
# Import the function that contains the business logic
from file_handler import process_dropped_files

class ImageUploaderGUI:
    """
    A class to create and manage the Drag and Drop GUI.
    It delegates file operations to an external handler.
    """
    def __init__(self, master, target_folder, allowed_extensions):
        """
        Initializes the GUI.
        :param master: The root tkinter window (must be a TkinterDnD.Tk() object).
        :param target_folder: The path to the folder where files will be copied.
        :param allowed_extensions: A list of allowed file extensions.
        """
        self.master = master
        self.target_folder = target_folder
        self.allowed_extensions = allowed_extensions

        self.master.title("AllegroBot - Image Uploader")
        self.master.geometry("600x400")

        drop_frame = tk.Frame(self.master, bd=2, relief="solid", bg="lightgrey")
        drop_frame.pack(fill="both", expand=True, padx=20, pady=20)

        info_label_text = f"Drag and drop {', '.join(self.allowed_extensions)} images here"
        info_label = tk.Label(drop_frame, text=info_label_text, bg="lightgrey", font=("Helvetica", 16))
        info_label.pack(padx=10, pady=10, expand=True)

        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

    def handle_drop(self, event):
        """
        Receives the drop event, delegates file processing, and shows results.
        """
        print(f"DEBUG: Raw event data: '{event.data}'")
        try:
            # 1. Get the list of file paths from the event
            file_paths = self.master.tk.splitlist(event.data)
        except tk.TclError:
            file_paths = [event.data]

        # 2. Delegate the actual file processing to the handler function
        copied_files, rejected_files = process_dropped_files(
            file_paths, self.target_folder, self.allowed_extensions
        )

        # 3. Display the results to the user
        self.show_feedback(copied_files, rejected_files)

    def show_feedback(self, copied_files, rejected_files):
        """Displays success and warning messages based on processing results."""
        if copied_files:
            copied_list_str = "\n".join(copied_files)
            messagebox.showinfo("Success", f"Successfully copied {len(copied_files)} image(s):\n\n{copied_list_str}")

        if rejected_files:
            rejected_list_str = "\n".join(rejected_files)
            messagebox.showwarning("Invalid Files", f"The following {len(rejected_files)} item(s) were not copied:\n\n{rejected_list_str}")