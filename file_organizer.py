# Building a visually enhanced "FileDeck" GUI using customtkinter
# This is a creative version with light/dark mode, emoji stats, and a modern desktop-style layout

import os
import shutil
from pathlib import Path
import customtkinter as ctk
from tkinter import filedialog, messagebox

# Define categories and extensions
FILE_CATEGORIES = {
    "📄 Documents": [".pdf", ".docx", ".doc", ".txt", ".pptx", ".xlsx"],
    "🖼️ Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp"],
    "🎞️ Videos": [".mp4", ".mkv", ".avi", ".mov"],
    "🎵 Audio": [".mp3", ".wav", ".aac"],
    "📦 Archives": [".zip", ".rar", ".tar", ".gz"],
    "💻 Scripts": [".py", ".js", ".html", ".css"],
    "❓ Others": []
}

# Function to classify file extension
def get_category(extension):
    for category, extensions in FILE_CATEGORIES.items():
        if extension.lower() in extensions:
            return category
    return "❓ Others"

# File organization logic
def organize_files(folder_path, update_callback):
    folder = Path(folder_path)
    category_counts = {cat: 0 for cat in FILE_CATEGORIES}

    for item in folder.iterdir():
        if item.is_file() and not item.name.startswith("."):
            category = get_category(item.suffix)
            category_folder = folder / category.strip("📄🖼️🎞️🎵📦💻❓").strip()
            category_folder.mkdir(exist_ok=True)

            # Avoid overwriting
            dest = category_folder / item.name
            count = 1
            while dest.exists():
                dest = category_folder / f"{item.stem}_{count}{item.suffix}"
                count += 1

            shutil.move(str(item), str(dest))
            category_counts[category] += 1
            update_callback(f"Moved: {item.name} → {category}")

    return category_counts

# GUI Application
class FileDeckApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🪟 FileDeck: Smart File Organizer")
        self.geometry("600x500")
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.selected_path = ctk.StringVar()

        # Header
        self.header = ctk.CTkLabel(self, text="📂 FileDeck Organizer", font=("Arial Rounded MT Bold", 22))
        self.header.pack(pady=20)

        # Path input
        self.path_frame = ctk.CTkFrame(self)
        self.path_frame.pack(pady=10, padx=20, fill="x")

        self.path_entry = ctk.CTkEntry(self.path_frame, width=400, textvariable=self.selected_path, placeholder_text="Select a folder...")
        self.path_entry.pack(side="left", padx=10, pady=10)

        self.browse_button = ctk.CTkButton(self.path_frame, text="Browse", command=self.browse_folder)
        self.browse_button.pack(side="right", padx=10)

        # Organize button
        self.organize_button = ctk.CTkButton(self, text="🚀 Organize Files", command=self.run_organizer, width=200)
        self.organize_button.pack(pady=10)

        # Stats Frame
        self.stats_box = ctk.CTkTextbox(self, height=180, width=500, font=("Segoe UI Emoji", 14))
        self.stats_box.pack(pady=10)
        self.stats_box.insert("end", "📊 Stats will appear here after organizing...\n")
        self.stats_box.configure(state="disabled")

        # Status Label
        self.status_label = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.status_label.pack(pady=10)

        # Theme Switch
        self.theme_switch = ctk.CTkSwitch(self, text="🌙 Dark Mode", command=self.toggle_theme)
        self.theme_switch.pack(pady=10)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.selected_path.set(path)
            self.status_label.configure(text="")

    def update_stats_box(self, message):
        self.stats_box.configure(state="normal")
        self.stats_box.insert("end", f"{message}\n")
        self.stats_box.configure(state="disabled")

    def run_organizer(self):
        folder = self.selected_path.get()
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("Error", "Please select a valid folder.")
            return

        self.stats_box.configure(state="normal")
        self.stats_box.delete("1.0", "end")
        self.stats_box.configure(state="disabled")

        counts = organize_files(folder, self.update_stats_box)
        self.update_stats_box("\n✅ Summary:")
        for cat, count in counts.items():
            if count > 0:
                self.update_stats_box(f"{cat}: {count} files")

        self.status_label.configure(text="🎉 All files organized successfully!")

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        ctk.set_appearance_mode("light" if current == "dark" else "dark")

# Launch app
app = FileDeckApp()
app.mainloop()

