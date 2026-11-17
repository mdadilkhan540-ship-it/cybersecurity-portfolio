# SCR - Python Cyber Security Toolkit

A Python-based desktop application that brings together practical cybersecurity utilities in a single Tkinter dashboard.

SCR is an educational project developed to explore cybersecurity concepts, automate common tasks, and practice security testing in controlled environments.

## Features

### 1. File & Folder Automation
- Create and write files.
- Read file contents.
- Organize folders by file type.

### 2. Hashing & Encryption
- Generate MD5 and SHA-256 hashes.
- Calculate file hashes.
- Generate and load Fernet encryption keys.
- Encrypt and decrypt text using Fernet.

### 3. API Tester
- Send HTTP requests.
- Test GET and POST requests.
- Configure custom headers.
- Submit JSON request bodies.
- View response status, execution time, and response body.

### 4. Networking Tools
- Scan a specified port range.
- Identify accessible ports.
- Discover subdomains.
- Stop an ongoing scan.

### 5. Offline Brute-Force Simulator
- Test a supplied hash against a local wordlist.
- Identify matching candidate passwords.
- Stop an ongoing operation.
- Generate a sample wordlist.

This module operates offline. It is intended for educational password-hashing demonstrations.

### 6. SQL Injection Tester
- Test a supplied URL parameter.
- Compare responses against a baseline.
- Send test payloads.
- Display potential SQL injection indicators.

**Note:** This is a detection aid, not a definitive vulnerability scanner.

### 7. Screenshot & Activity Logging
- Capture desktop screenshots.
- Save screenshots locally.
- View recent application activity.
- Refresh the activity log.

## Technology Stack

- Python
- Tkinter
- Requests
- Cryptography
- PyAutoGUI
- Pillow
- Flask
- SQLite
- JSON
- Socket programming
- Hashlib

## Project Structure

```text
cyber_toolkit_complete/
│
├── main.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── data/
│   └── sample_wordlist.txt
│
├── logs/                  # Generated locally, not committed
│
├── modules/
│   ├── api_tester.py
│   ├── bruteforce.py
│   ├── file_automation.py
│   ├── hash_crypto.py
│   ├── network_tools.py
│   ├── screenshot_tool.py
│   ├── sql_tester.py
│   └── __init__.py
│
├── test_server/
│   └── vulnerable_app.py
│
└── utils/
    ├── logger.py
    └── __init__.py
```

## Installation

### Prerequisites

- Python 3.10 or later
- Git
- Windows, Linux, or macOS with a supported Tkinter installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/python-cyber-toolkit.git
```

### 2. Enter the project directory

```bash
cd python-cyber-toolkit
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On Linux/macOS:

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Launch the application

```bash
python main.py
```

## Local SQL Injection Practice Server

SCR includes a deliberately vulnerable Flask application for testing the SQL Injection Tester in a controlled localhost environment.

Start the practice server:

```bash
python test_server/vulnerable_app.py
```

Open the following local endpoint:

```text
http://127.0.0.1:5050/user?id=1
```

Use this URL in the SQL Injection Tester module.

**Important:** This practice application intentionally contains an unsafe SQL query. Never deploy it publicly or expose it to an untrusted network.

## Testing and Validation

The project has undergone developer-reported functional testing.

Reported test coverage includes:

- Python syntax compilation.
- Application startup and navigation.
- File operations.
- Hashing and encryption.
- API request handling.
- Networking operations.
- Offline hash testing.
- Local SQL injection testing.
- Screenshot capture and activity logging.
- Dependency and integration checks.

All ten reported testing stages were completed successfully.

These results represent development testing, not an independent security audit or certification.

## Security and Responsible Usage

- Only test systems that you own or have explicit authorization to assess.
- Keep encryption keys and credentials private.
- Do not upload local logs, screenshots containing private information, or encryption keys.
- Use the brute-force simulator only with hashes and wordlists you are authorized to test.
- Keep the intentionally vulnerable Flask server restricted to localhost.
- MD5 is included for educational and legacy-hash demonstrations. It is not suitable for password storage.

## Project Purpose

SCR was developed as a practical learning project to explore Python programming, desktop application development, cybersecurity utilities, networking, cryptography, and security testing.

## License

No license has been selected yet. All rights are reserved unless a license is added to this repository.

## Author

Developed as a Python and Cybersecurity learning project.