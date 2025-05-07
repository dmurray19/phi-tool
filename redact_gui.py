import tkinter as tk
from tkinter import filedialog, messagebox
import mysql.connector
import os
import tempfile
from redact_phi import redact_phi  # assumes redact_phi is in the same folder or PYTHONPATH

# Database connection config
db_config = {
    'host': 'localhost',
    'user': 'myphi',
    'password': 'myphi',
    'database': 'mysqlphi'
}

# GUI-based app
class PHIRedactorApp:
    def __init__(self, master):
        self.master = master
        master.title("PHI Redaction App")

        self.label = tk.Label(master, text="   Upload a medical record file to redact PHI   ")
        self.label.pack(pady=10)

        self.omit_options = [
            "name", "dob", "mrn", "ssn", "address", "phone", "email", "fax", "insurance",
            "group", "url", "ip", "device", "serial", "code", "hospital", "license",
            "certificate", "beneficiary", "account", "labs", "allergy", "biometric", "doctor", "patient"
        ]
        self.omit_vars = {opt: tk.BooleanVar() for opt in self.omit_options}

        self.omit_button = tk.Button(master, text="Select PHI to Omit", command=self.open_omit_window)
        self.omit_button.pack(pady=5)

        self.custom_allergies = []

        self.allergy_button = tk.Button(master, text="Enter Custom Allergies", command=self.open_allergy_window)
        self.allergy_button.pack(pady=5)

        self.upload_button = tk.Button(master, text="Upload File", command=self.upload_file)
        self.upload_button.pack(pady=5)

        self.download_button = tk.Button(master, text="Download Redacted File", command=self.download_file, state=tk.DISABLED)
        self.download_button.pack(pady=5)

        self.reidentify_button = tk.Button(master, text="Reidentify Record", command=self.open_reidentify_window)
        self.reidentify_button.pack(pady=5)

        self.last_output_path = None  # Store latest redacted file

    def open_omit_window(self):
        top = tk.Toplevel(self.master)
        top.title("Select PHI Types to Omit")

        tk.Label(top, text="  Check any identifier to omit redaction  ").pack(pady=5)

        for key, var in self.omit_vars.items():
            cb = tk.Checkbutton(top, text=key, variable=var)
            cb.pack(anchor="w", padx=10)

        tk.Button(top, text="Done", command=top.destroy).pack(pady=5)

    def open_allergy_window(self):
        top = tk.Toplevel(self.master)
        top.title("Custom Allergies")

        tk.Label(top, text="Enter allergy names to redact, one per line.").pack(pady=5)
        
        text_box = tk.Text(top, width=40, height=10)
        text_box.pack(padx=10)

        def save_allergies():
            raw = text_box.get("1.0", tk.END)
            self.custom_allergies = [line.strip() for line in raw.splitlines() if line.strip()]
            top.destroy()

        tk.Button(top, text="Save", command=save_allergies).pack(pady=5)

    def upload_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if not filepath:
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_output:
            tmp_output_path = tmp_output.name

        try:
            omit_selection = {opt for opt, var in self.omit_vars.items() if var.get()}

            record_id, key, encrypted_data = redact_phi(filepath, tmp_output_path, exclude_options=omit_selection, custom_allergies=self.custom_allergies)
            self.save_to_db(record_id, key.decode(), encrypted_data.decode())

            self.last_output_path = tmp_output_path
            self.download_button.config(state=tk.NORMAL)  # Enable download button

            messagebox.showinfo("Success", f"File redacted.\nRecord ID: {record_id}")
        except Exception as e:
            messagebox.showerror("Error", f"Redaction failed: {e}")
            if os.path.exists(tmp_output_path):
                os.remove(tmp_output_path)
            self.last_output_path = None
            self.download_button.config(state=tk.DISABLED)

    def download_file(self):
        if not self.last_output_path or not os.path.exists(self.last_output_path):
            messagebox.showerror("Error", "No redacted file available to download.")
            return

        save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if save_path:
            try:
                with open(self.last_output_path, 'r') as src, open(save_path, 'w') as dst:
                    dst.write(src.read())
                messagebox.showinfo("Downloaded", f"Redacted file saved to:\n{save_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def save_to_db(self, record_id, key, encrypted):
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO redacted_records (record_id, encryption_key, encrypted_phi)
            VALUES (%s, %s, %s)
        """, (record_id, key, encrypted))
        conn.commit()
        cursor.close()
        conn.close()

    def open_reidentify_window(self):
        popup = tk.Toplevel(self.master)
        popup.title("Reidentify PHI Record")

        tk.Label(popup, text="Enter Record ID:").pack(pady=5)
        record_entry = tk.Entry(popup, width=40)
        record_entry.pack(pady=2)

        tk.Label(popup, text="Select Deidentified File:").pack(pady=5)

        selected_file = tk.StringVar()
        file_entry = tk.Entry(popup, textvariable=selected_file, width=40)
        file_entry.pack(pady=2)

        def browse_file():
            filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if filepath:
                selected_file.set(filepath)

        tk.Button(popup, text="Browse", command=browse_file).pack(pady=2)

    def open_reidentify_window(self):
        popup = tk.Toplevel(self.master)
        popup.title("Reidentify PHI Record")

        tk.Label(popup, text="Select Deidentified File:").pack(pady=5)

        selected_file = tk.StringVar()
        file_entry = tk.Entry(popup, textvariable=selected_file, width=40)
        file_entry.pack(pady=2)

        def browse_file():
            filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if filepath:
                selected_file.set(filepath)

        tk.Button(popup, text="Browse", command=browse_file).pack(pady=2)

        def perform_reidentify():
            file_path = selected_file.get().strip()
            if not file_path or not os.path.exists(file_path):
                messagebox.showerror("Error", "Please select a valid deidentified file.")
                return

            try:
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    if not lines:
                        raise Exception("File is empty.")
                    record_id = lines[0].strip()
                    content = "".join(lines[1:])  # skip the record ID line

                conn = mysql.connector.connect(**db_config)
                cursor = conn.cursor()
                cursor.execute("SELECT encryption_key, encrypted_phi FROM redacted_records WHERE record_id = %s", (record_id,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()

                if not result:
                    messagebox.showerror("Error", f"No record found for ID: {record_id}")
                    return

                key, encrypted_phi = result
                from cryptography.fernet import Fernet
                cipher_suite = Fernet(key.encode())
                decrypted = cipher_suite.decrypt(encrypted_phi.encode()).decode()

                # build reidentification map from *label*|value format
                replacements = {}
                for line in decrypted.splitlines():
                    if "|" in line:
                        tag, value = line.split("|", 1)
                        replacements[tag.strip()] = value.strip()   

                for tag, original in replacements.items():
                    content = content.replace(tag, original)

                save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
                if save_path:
                    with open(save_path, "w") as out:
                        out.write(content)
                    messagebox.showinfo("Success", f"Reidentified file saved to:\n{save_path}")
                popup.destroy()

            except Exception as e:
                messagebox.showerror("Error", f"Reidentification failed: {e}")

        tk.Button(popup, text="Reidentify", command=perform_reidentify).pack(pady=10)

# GUI runner
if __name__ == "__main__":
    root = tk.Tk()
    app = PHIRedactorApp(root)
    root.mainloop()