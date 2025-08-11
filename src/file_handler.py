import os
import shutil


def process_dropped_files(file_paths, target_folder, allowed_extensions):
    """
    Validates a list of file paths and copies valid files to a target folder.
    (This function remains unchanged)
    """
    copied_files = []
    rejected_files = []

    for file_path in file_paths:
        clean_path = file_path.strip()
        if not clean_path:
            continue

        file_name = os.path.basename(clean_path)

        try:
            if os.path.isfile(clean_path):
                _, file_extension = os.path.splitext(file_name)

                if file_extension.lower() in allowed_extensions:
                    destination_path = os.path.join(target_folder, file_name)
                    shutil.copy(clean_path, destination_path)
                    copied_files.append(file_name)
                else:
                    rejected_files.append(file_name)
            else:
                rejected_files.append(file_name + " (Not a file)")
        except Exception as e:
            print(f"Error processing {clean_path}: {e}")
            rejected_files.append(f"{file_name} (Error: {e})")

    return copied_files, rejected_files


def clear_folder_contents(folder_path):
    """
    Deletes all files within a specified folder.

    :param folder_path: The absolute path to the folder to be cleared.
    """
    print(f"Czyszczenie zawartości folderu: {folder_path}")
    if not os.path.isdir(folder_path):
        print("Folder nie został znaleziony, pomijanie czyszczenia.")
        return

    # Iterate over all the items in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            # Check if it is a file and then remove it
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.remove(file_path)
                print(f"Usunięto: {filename}")
        except Exception as e:
            print(f"Błąd podczas usuwania pliku {file_path}. Powód: {e}")

    print("Zakończono czyszczenie.")