import os
from tkinterdnd2 import TkinterDnD
from gui import ImageUploaderGUI
from file_handler import clear_folder_contents


def ensure_folder_exists(folder_path):
    """Tworzy folder, jeśli nie istnieje."""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Utworzono folder: {folder_path}")


def main():
    """Główna funkcja konfigurująca i uruchamiająca aplikację."""
    # --- Konfiguracja ---
    ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg']

    # --- Ustawienie ścieżek ---
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
    TARGET_FOLDER = os.path.join(PROJECT_ROOT, "images", "input")
    OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "output")  # Nowy folder na wyniki

    ensure_folder_exists(TARGET_FOLDER)
    ensure_folder_exists(OUTPUT_FOLDER)  # Upewnij się, że folder output istnieje

    # --- Uruchomienie Aplikacji ---
    root = TkinterDnD.Tk()
    # Przekaż ścieżkę do folderu z wynikami do GUI
    app = ImageUploaderGUI(root, TARGET_FOLDER, ALLOWED_EXTENSIONS, OUTPUT_FOLDER)

    def on_closing():
        print("Zamykanie aplikacji...")
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

    # Wyczyść folder z obrazami po zamknięciu
    clear_folder_contents(TARGET_FOLDER)
    print("Aplikacja zamknięta.")


if __name__ == "__main__":
    main()