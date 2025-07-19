import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import ttk
from tkinter.scrolledtext import ScrolledText
import json

# CONFIG & LOGGING

CONFIG_FILE = "config.json"

DEFAULT_FILE_TYPES = {
    "Documents": [".pdf", ".docx", ".doc", ".txt", ".xls", ".xlsx", ".ppt", ".pptx"],
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv"],
    "Music": [".mp3", ".wav", ".flac"],
}

if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
else:
    config = {
        "file_types": DEFAULT_FILE_TYPES,
        "last_folder": "",
        "theme": "flatly"  # default light theme
    }

log_handler = RotatingFileHandler('organizer.log', maxBytes=50000, backupCount=3)
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ORGANIZER LOGIC

category_counts = {}

def get_category(extension):
    for category, extensions in config["file_types"].items():
        if extension.lower() in extensions:
            return category
    return "Others"

def count_files(target_dir, include_subfolders):
    total = 0
    if include_subfolders:
        for root, dirs, files in os.walk(target_dir):
            total += len(files)
    else:
        total = len([name for name in os.listdir(target_dir) if os.path.isfile(os.path.join(target_dir, name))])
    return total

def organize_files(target_dir, include_subfolders, delete_empty, progress_var, progress_bar):
    global category_counts
    category_counts = {cat: 0 for cat in config["file_types"].keys()}
    category_counts["Others"] = 0

    try:
        total_files = count_files(target_dir, include_subfolders)
        processed = 0

        walker = os.walk(target_dir) if include_subfolders else [(target_dir, [], os.listdir(target_dir))]

        for root, dirs, files in walker:
            for file in files:
                file_path = os.path.join(root, file)
                if not os.path.isfile(file_path):
                    continue

                _, ext = os.path.splitext(file)
                category = get_category(ext)
                category_folder = os.path.join(target_dir, category)
                os.makedirs(category_folder, exist_ok=True)
                dest_path = os.path.join(category_folder, file)

                try:
                    if os.path.abspath(file_path) != os.path.abspath(dest_path):
                        shutil.move(file_path, dest_path)
                        logging.info(f"Moved: {file} --> {category}/")
                        category_counts[category] += 1
                        status_text.insert(tk.END, f"Moved: {file} → {category}/\n")
                        status_text.see(tk.END)
                except Exception as e:
                    logging.error(f"Error moving file {file_path}: {e}")

                processed += 1
                progress = int((processed / total_files) * 100)
                progress_var.set(progress)
                progress_bar.update_idletasks()

        if delete_empty:
            remove_empty_folders(target_dir)

        logging.info("✅ Organizing complete.")
        config["last_folder"] = target_dir
        save_config()

        summary = f"✅ Organizing Complete!\n\nTotal files: {processed}\n"
        for cat, count in category_counts.items():
            if count > 0:
                summary += f"{cat}: {count}\n"

        logging.info(summary)
        messagebox.showinfo("Summary", summary)

    except Exception as e:
        logging.error(f"Unhandled error: {e}")
        messagebox.showerror("Error", f"Something went wrong: {e}")

def remove_empty_folders(folder):
    for root, dirs, files in os.walk(folder, topdown=False):
        for d in dirs:
            dir_path = os.path.join(root, d)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
                    logging.info(f"Deleted empty folder: {dir_path}")
            except Exception as e:
                logging.error(f"Could not delete folder {dir_path}: {e}")

def save_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

# GUI ACTIONS

def start_organizing():
    folder_selected = filedialog.askdirectory(initialdir=config.get("last_folder", ""))
    if folder_selected:
        include_subfolders = subfolder_var.get()
        delete_empty = delete_empty_var.get()
        progress_var.set(0)
        status_text.delete(1.0, tk.END)  # clear old status
        organize_files(folder_selected, include_subfolders, delete_empty, progress_var, progress_bar)

def add_category():
    new_category = simpledialog.askstring("Add Category", "Enter new category name:")
    if new_category:
        if new_category in config["file_types"]:
            messagebox.showinfo("Exists", f"'{new_category}' already exists.")
        else:
            config["file_types"][new_category] = []
            save_config()
            update_category_dropdown()
            messagebox.showinfo("Added", f"'{new_category}' category added.")

def add_extension_to_category():
    selected_category = category_var.get()
    if not selected_category or selected_category not in config["file_types"]:
        messagebox.showerror("Error", "Please select a valid category first.")
        return

    ext = simpledialog.askstring("Extension", "Enter new file extension (include dot, e.g., .log):")
    if ext:
        if not ext.startswith("."):
            ext = "." + ext
        if ext.lower() in config["file_types"][selected_category]:
            messagebox.showinfo("Exists", f"Extension '{ext}' already exists in '{selected_category}'.")
        else:
            config["file_types"][selected_category].append(ext.lower())
            save_config()
            messagebox.showinfo("Added", f"Extension '{ext}' added to '{selected_category}'.")

def update_category_dropdown():
    category_dropdown["values"] = list(config["file_types"].keys())
    if config["file_types"]:
        category_var.set(list(config["file_types"].keys())[0])

def toggle_theme():
    if theme_var.get():
        config["theme"] = "superhero"
    else:
        config["theme"] = "flatly"
    save_config()
    apply_theme()

def apply_theme():
    style.theme_use(config["theme"])
    theme_var.set(config["theme"] == "superhero")

# GUI SETUP with ttkbootstrap

root = tk.Tk()
root.title("📂 File Organizer SuperPro")
root.geometry("500x600")

style = Style(theme=config.get("theme", "flatly"))

label = ttk.Label(root, text="Organize Files by Type", font=("Arial", 16))
label.pack(pady=10)

subfolder_var = tk.BooleanVar(value=False)
subfolder_checkbox = ttk.Checkbutton(root, text="Include Subfolders", variable=subfolder_var)
subfolder_checkbox.pack()

delete_empty_var = tk.BooleanVar(value=False)
delete_empty_checkbox = ttk.Checkbutton(root, text="Delete Empty Folders", variable=delete_empty_var)
delete_empty_checkbox.pack()

select_button = ttk.Button(root, text="Select Folder and Organize", command=start_organizing, bootstyle=SUCCESS)
select_button.pack(pady=10)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var, bootstyle=INFO)
progress_bar.pack(pady=10)

status_text = ScrolledText(root, height=10, width=55)
status_text.pack(pady=10)

add_cat_button = ttk.Button(root, text="➕ Add New Category", command=add_category)
add_cat_button.pack(pady=5)

category_var = tk.StringVar(value=next(iter(config["file_types"].keys()), ""))
category_dropdown = ttk.Combobox(root, textvariable=category_var, state="readonly")
category_dropdown.pack(pady=5)

add_ext_button = ttk.Button(root, text="➕ Add Extension to Selected Category", command=add_extension_to_category)
add_ext_button.pack(pady=5)

theme_var = tk.BooleanVar(value=config.get("theme", "flatly") == "superhero")
theme_checkbox = ttk.Checkbutton(root, text="Dark Mode", variable=theme_var, command=toggle_theme)
theme_checkbox.pack(pady=10)

update_category_dropdown()
apply_theme()

root.mainloop()
