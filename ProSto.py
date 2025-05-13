import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

# Пути к скриптам сборки
CSS_BUILDER = "css.py"
HTML_BUILDER = "html.py"
JS_BUILDER = "js.py"  # на будущее

# Директория для отслеживания
WATCH_DIR = "src"

class BuilderHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            file_path = event.src_path
            if file_path.endswith('.sass') or file_path.endswith('.scss'):
                print(f"Detected SASS change: {file_path}")
                subprocess.run(["python3", CSS_BUILDER], check=True)
            elif file_path.endswith('.html'):
                print(f"Detected HTML change: {file_path}")
                subprocess.run(["python3", HTML_BUILDER], check=True)
            elif file_path.endswith('.js'):
                print(f"Detected JS change: {file_path}")
                subprocess.run(["python3", JS_BUILDER], check=True)

def main():
    event_handler = BuilderHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_DIR, recursive=True)
    observer.start()

    print(f"Watching for changes in {WATCH_DIR}...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
