import os
from tkinterdnd2 import TkinterDnD
from gui import ImageUploaderGUI


def ensure_folder_exists(folder_path):
    """Creates a folder if it doesn't already exist."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")


def main():
    """
    Main function to configure and run the application.
    """
    # --- Configuration ---
    ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg']

    # --- Path Setup ---
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    TARGET_FOLDER = os.path.join(PROJECT_ROOT, "images", "input")

    ensure_folder_exists(TARGET_FOLDER)

    # --- Application Startup ---
    root = TkinterDnD.Tk()

    app = ImageUploaderGUI(root, TARGET_FOLDER, ALLOWED_EXTENSIONS)

    # --- FIX: Define what happens when the window is closed ---
    def on_closing():
        """
        This function is called when the user clicks the 'X' button.
        It ensures the application exits cleanly.
        """
        print("Closing application...")
        root.quit()  # Stops the tkinter mainloop
        root.destroy()  # Destroys the window and its widgets

    # Intercept the window close event and call the on_closing function
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the main event loop
    root.mainloop()

    print("Application closed.")


if __name__ == "__main__":
    main()