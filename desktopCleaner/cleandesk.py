import os
import time
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class DesktopHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        elif event.event_type == 'created':
            self.handle_file(event.src_path)

    def scan_desktop(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        for filename in os.listdir(desktop_path):
            file_path = os.path.join(desktop_path, filename)
            if os.path.isfile(file_path):
                self.handle_file(file_path)

    def handle_file(self, file_path):
        # Introduce a short delay to allow the file creation process to complete
        time.sleep(1)

        print(f"File detected: {file_path}")

        # Specify the path to the 'Deski' folder on the desktop
        deski_folder = os.path.join(os.path.expanduser("~"), "Desktop", "Deski")

        # Ensure the 'Deski' folder exists, create if not
        if not os.path.exists(deski_folder):
            os.makedirs(deski_folder)

        # Check if the file is a folder
        if os.path.isdir(file_path):
            return

        # Check file extensions and move to appropriate subfolder
        file_extension = os.path.splitext(file_path)[1].lower()

        if "screenshot" in os.path.basename(file_path).lower() or "screen shot" in os.path.basename(file_path).lower():
            subfolder_path = os.path.join(deski_folder, "Screenshots")
        elif file_extension in {'.png', '.jpg', '.jpeg', '.gif'}:
            subfolder_path = os.path.join(deski_folder, "Images")
        elif file_extension == '.pdf':
            subfolder_path = os.path.join(deski_folder, "PDF")
        elif "invoice" in os.path.basename(file_path).lower():
            if "out" in os.path.basename(file_path).lower():
                subfolder_path = os.path.join(deski_folder, "Invoices", "Out")
            else:
                subfolder_path = os.path.join(deski_folder, "Invoices", "In")
        elif file_extension in {'.pages', '.doc', '.docx'}:
            subfolder_path = os.path.join(deski_folder, "Docs")
        else:
            subfolder_path = os.path.join(deski_folder, "Random")

        # Ensure the subfolder exists, create if not
        if not os.path.exists(subfolder_path):
            os.makedirs(subfolder_path)

        # Move the file to the destination subfolder
        new_location = os.path.join(subfolder_path, os.path.basename(file_path))
        try:
            shutil.move(file_path, new_location)
            print(f"File moved to {subfolder_path}: {new_location}")
        except Exception as e:
            print(f"Error moving file: {e}")

    def on_moved(self, event):
        if event.is_directory:
            return
        elif event.event_type == 'moved':
            self.handle_file(event.dest_path)


def start_monitoring():
    event_handler = DesktopHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.join(os.path.expanduser("~"), "Desktop"), recursive=False)
    observer.start()

    try:
        while True:
            # Scan the desktop periodically to handle existing files
            event_handler.scan_desktop()
            time.sleep(10)  # Adjust the interval as needed
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    print("Desktop cleaner is running. Press Ctrl+C to stop.")
    start_monitoring()
