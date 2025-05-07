# PHI Redaction Tool – GUI Edition

This is a simple Python GUI application for detecting and redacting Protected Health Information (PHI) from text-based medical records. It allows users to upload files, customize redaction options, save encrypted data to a MySQL database, and optionally re-identify redacted files.

## Features

- Redact over two dozen PHI categories using regex
- Selectively omit specific PHI types via checkboxes
- Define custom allergy terms to redact
- Save redacted records to MySQL (record ID, encryption key, encrypted data)
- Download redacted files
- Reidentify PHI using record ID and database retrieval

## Requirements

- Python 3.7+
- MySQL database
- Dependencies:
  - `mysql-connector-python`
  - `cryptography`

Install dependencies using:

```bash
pip install mysql-connector-python cryptography
```

## File Structure

Place both scripts in the same folder:

```
project-folder/
├── redact_gui.py
└── redact_phi.py
```

## Usage

Run the GUI:

```bash
python redact_gui.py
```

### Redacting a File

1. Click **"Select PHI to Omit"** to choose which PHI fields should be excluded from redaction.
2. Click **"Enter Custom Allergies"** to define allergy terms to be redacted.
3. Click **"Upload File"** to select a `.txt` file for redaction.
4. A redacted file is generated and stored temporarily.
5. Click **"Download Redacted File"** to save the output.
6. The encrypted PHI is stored in the MySQL database.

### Reidentifying a File

1. Click **"Reidentify Record"**.
2. Enter the **record ID**.
3. Select the **deidentified `.txt` file**.
4. The app will query the database, decrypt the PHI, and restore it in the file.
5. Save the reidentified file to your desired location.

## Database Setup

Create a table in your MySQL database:

```sql
CREATE TABLE redacted_records (
    record_id VARCHAR(255) PRIMARY KEY,
    encryption_key TEXT NOT NULL,
    encrypted_phi TEXT NOT NULL
);
```

Update the `db_config` section in `redact_gui.py` with your own MySQL credentials.

```python
db_config = {
    'host': 'localhost',
    'user': 'myphi',
    'password': 'myphi',
    'database': 'mysqlphi'
}
```

## Notes

- The application uses AES encryption via the `cryptography` package (Fernet) to secure PHI before storing it.
- Temporary files are safely managed and cleaned up automatically.

## License

MIT License – for educational and demonstration purposes.
