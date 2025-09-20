import re
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import filedialog, messagebox
import csv

# --- Functions for extracting actions ---
def parse_deadline(deadline_raw):
    today = datetime(2025, 9, 20)
    deadline_raw = deadline_raw.lower().strip()

    if 'asap' in deadline_raw or 'as soon as possible' in deadline_raw:
        return 'ASAP'

    if 'next' in deadline_raw:
        days_ahead = 0
        weekdays = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday']
        for i, day in enumerate(weekdays):
            if day in deadline_raw:
                days_ahead = (i - today.weekday() + 7) % 7 or 7
        return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')

    try:
        if len(deadline_raw.split()) == 2:
            month, day = deadline_raw.split()
            year = today.year
            return datetime.strptime(f"{month} {day} {year}", '%B %d %Y').strftime('%Y-%m-%d')
    except ValueError:
        pass

    return deadline_raw

def extract_actions(notes):
    actions = []
    lines = notes.split('\n')
    pattern = r'([A-Z][a-z]+)\s+(will|to|needs to|should)\s+(.+?)(?:\s+by\s+([A-Za-z0-9\s]+)|\s+(as soon as possible|ASAP))\.?$'

    for line in lines:
        line = line.strip()
        if not line:
            continue
        match = re.search(pattern, line, re.IGNORECASE)
        if match:
            person = match.group(1)
            verb = match.group(2)
            task = match.group(3).strip()
            deadline_raw = match.group(4) if match.group(4) else (match.group(5) if match.group(5) else "ASAP")
            deadline = parse_deadline(deadline_raw)
            actions.append({
                'person': person,
                'task': f"{verb} {task}".strip(),
                'deadline': deadline
            })
    return actions

# --- GUI Functions ---
notes_file = None
actions_data = []

def select_file():
    global notes_file
    notes_file = filedialog.askopenfilename(
        title="Select Notes File",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    if notes_file:
        messagebox.showinfo("Selected File", f"You selected:\n{notes_file}")

def extract_actions_gui():
    global actions_data
    if not notes_file:
        messagebox.showwarning("No file", "Please select a notes file first.")
        return
    with open(notes_file, 'r') as f:
        notes = f.read()
    actions_data = extract_actions(notes)
    if actions_data:
        messagebox.showinfo("Actions Extracted", f"{len(actions_data)} actions found!")
    else:
        messagebox.showinfo("No Actions", "No actions found in this file.")

def save_to_csv():
    if not actions_data:
        messagebox.showwarning("No actions", "No actions to save.")
        return
    save_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save Actions CSV"
    )
    if save_path:
        keys = actions_data[0].keys()
        with open(save_path, 'w', newline='') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(actions_data)
        messagebox.showinfo("Saved", f"Actions saved to {save_path}")

# --- Colorful Tkinter GUI ---
root = tk.Tk()
root.title("Meeting Action Tracker")
root.geometry("450x300")
root.configure(bg="#e6f2ff")  # light blue background

# Title label
title_label = tk.Label(root, text="Meeting Action Tracker", font=("Helvetica", 18, "bold"),
                       bg="#e6f2ff", fg="#003366")
title_label.pack(pady=15)

# Frame for buttons
button_frame = tk.Frame(root, bg="#e6f2ff")
button_frame.pack(pady=20)

# Buttons with colors
tk.Button(button_frame, text="Select Notes File", command=select_file, width=25,
          bg="#4caf50", fg="white", font=("Arial", 12, "bold"), activebackground="#45a049").pack(pady=10)

tk.Button(button_frame, text="Extract Actions", command=extract_actions_gui, width=25,
          bg="#2196f3", fg="white", font=("Arial", 12, "bold"), activebackground="#0b7dda").pack(pady=10)

tk.Button(button_frame, text="Save to CSV", command=save_to_csv, width=25,
          bg="#ff5722", fg="white", font=("Arial", 12, "bold"), activebackground="#e64a19").pack(pady=10)

root.mainloop()
