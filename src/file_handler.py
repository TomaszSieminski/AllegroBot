import os
import shutil


def process_dropped_files(file_paths, target_folder, allowed_extensions):
    """
    Validates a list of file paths and copies valid files to a target folder.

    :param file_paths: A list of absolute paths to the files.
    :param target_folder: The destination folder for copied files.
    :param allowed_extensions: A list of allowed file extensions.
    :return: A tuple containing two lists: (copied_files, rejected_files)
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
                    # File has a valid path but wrong extension
                    rejected_files.append(file_name)
            else:
                # Dropped item is not a file (e.g., a folder)
                rejected_files.append(file_name + " (Not a file)")
        except Exception as e:
            # Handle potential errors during file processing
            print(f"Error processing {clean_path}: {e}")
            rejected_files.append(f"{file_name} (Error: {e})")

    return copied_files, rejected_files