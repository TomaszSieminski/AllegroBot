import tkinter as tk
from tkinterdnd2 import DND_FILES
from tkinter import messagebox
import os
import json
from file_handler import process_dropped_files
from image_processor import analyze_image_for_serial_number

# --- POPRAWKA: Importujemy klasę AllegroAPIClient, a nie funkcję search_offers ---
from allegro_api import AllegroAPIClient


class ImageUploaderGUI:
    def __init__(self, master, target_folder, allowed_extensions, output_folder):
        self.master = master
        self.target_folder = target_folder
        self.output_folder = output_folder
        self.allowed_extensions = allowed_extensions

        self.master.title("AllegroBot")
        self.master.geometry("600x650")

        # --- Drop Frame ---
        drop_frame = tk.Frame(self.master, bd=2, relief="solid", bg="lightgrey")
        drop_frame.pack(fill="both", expand=True, padx=20, pady=20)
        info_label = tk.Label(drop_frame, text=f"Przeciągnij i upuść obrazy ({', '.join(self.allowed_extensions)})",
                              bg="lightgrey", font=("Helvetica", 16))
        info_label.pack(padx=10, pady=10, expand=True)
        drop_frame.drop_target_register(DND_FILES)
        drop_frame.dnd_bind('<<Drop>>', self.handle_drop)

        # --- Pole wyników analizy ---
        results_frame = tk.Frame(self.master, padx=20)
        results_frame.pack(fill='x', expand=True)
        results_label = tk.Label(results_frame, text="Wyniki Analizy (możesz edytować):", font=("Helvetica", 10))
        results_label.pack(anchor='w')
        self.results_text = tk.Text(results_frame, height=10, font=("Courier New", 10), relief="solid", bd=1)
        self.results_text.pack(fill='x', expand=True, pady=(0, 10))

        # --- Ramka na przyciski ---
        button_frame = tk.Frame(self.master)
        button_frame.pack(fill='x', padx=20, pady=(0, 10))

        analyze_button = tk.Button(button_frame, text="1. Analizuj Zdjęcia", font=("Helvetica", 12),
                                   command=self.trigger_analysis)
        analyze_button.pack(pady=5, fill='x')

        search_button = tk.Button(button_frame, text="2. Wyszukaj produkty w Allegro", font=("Helvetica", 12),
                                  command=self.trigger_allegro_search)
        search_button.pack(pady=5, fill='x')

    def trigger_allegro_search(self):
        content = self.results_text.get("1.0", tk.END)
        queries = [line.strip() for line in content.splitlines() if
                   line.strip() and "None" not in line and "Error" not in line]

        if not queries:
            messagebox.showwarning("Brak numerów",
                                   "Pole wyników jest puste lub nie zawiera prawidłowych numerów seryjnych do wyszukania.")
            return

        print("\n--- Rozpoczynanie wyszukiwania w Allegro ---")
        messagebox.showinfo("Wyszukiwanie...",
                            f"Rozpoczynam wyszukiwanie dla {len(queries)} numerów. To może chwilę potrwać...")

        try:
            allegro_client = AllegroAPIClient()
        except (FileNotFoundError, ValueError) as e:
            messagebox.showerror("Błąd Konfiguracji", str(e))
            return

        all_results = {}
        for query in queries:
            self.master.update_idletasks()
            offers = allegro_client.search_offers(query)

            if offers is not None:
                if len(offers) > 0:
                    print(f"✅ Sukces: Znaleziono {len(offers)} ofert dla '{query}'.")
                    all_results[query] = offers
                else:
                    print(f"🟡 Informacja: Nie znaleziono żadnych aktywnych ofert dla '{query}'.")
                    all_results[query] = []
            else:
                print(f"❌ Błąd: Nie udało się wyszukać ofert dla '{query}'. Sprawdź logi powyżej.")
                all_results[query] = "API_ERROR"

        if not all_results:
            messagebox.showerror("Błąd", "Nie udało się pobrać żadnych ofert. Sprawdź konsolę, aby zobaczyć błędy.")
            return

        output_path = os.path.join(self.output_folder, "allegro_results.json")
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_results, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Sukces", f"Zapisano wszystkie wyniki do pliku:\n{output_path}")
            print(f"--- Wyszukiwanie zakończone. Wyniki zapisano w {output_path} ---")
        except Exception as e:
            messagebox.showerror("Błąd zapisu", f"Nie udało się zapisać pliku z wynikami. Błąd: {e}")

    def trigger_analysis(self):
        self.results_text.delete('1.0', tk.END)
        print("\n--- Rozpoczynanie analizy zdjęć ---")
        image_files = [f for f in os.listdir(self.target_folder) if f.lower().endswith(tuple(self.allowed_extensions))]
        if not image_files:
            messagebox.showinfo("Brak zdjęć", "Folder docelowy jest pusty. Przeciągnij i upuść zdjęcia, aby je dodać.")
            return
        print(f"Znaleziono {len(image_files)} zdjęć. Analiza może chwilę potrwać...")
        for filename in image_files:
            image_path = os.path.join(self.target_folder, filename)
            print(f"Analizowanie: {filename}...")
            serial_number = analyze_image_for_serial_number(image_path)
            result_line = f"{serial_number}\n"
            self.results_text.insert(tk.END, result_line)
            print(f"Wynik dla {filename}: {serial_number}")
            self.master.update_idletasks()
        print("--- Analiza zakończona ---")
        messagebox.showinfo("Analiza Zakończona",
                            "Zakończono analizowanie zdjęć. Wyniki są dostępne w oknie aplikacji.")

    def handle_drop(self, event):
        self.results_text.delete('1.0', tk.END)
        try:
            file_paths = self.master.tk.splitlist(event.data)
        except tk.TclError:
            file_paths = [event.data]
        copied_files, rejected_files = process_dropped_files(
            self.target_folder, self.allowed_extensions, file_paths
        )
        self.show_feedback(copied_files, rejected_files)

    def show_feedback(self, copied_files, rejected_files):
        if copied_files:
            messagebox.showinfo("Sukces", f"Pomyślnie skopiowano {len(copied_files)} obraz(ów).")
        if rejected_files:
            messagebox.showwarning("Nieprawidłowe pliki",
                                   f"{len(rejected_files)} następujące(ych) elementów nie skopiowano.")