# Setup & Installation

This guide covers how to set up the development environment for PekoCMS.

## Prerequisites
- Python 3.10 or higher
- Windows OS (recommended for full compatibility)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd nidaan-polyclinic-cms
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

## Initial Configuration
Run the setup script to verify environment and create necessary directories:

```bash
python setup.py
```

This script will:
- Create `assets/` directory (if missing)
- Create `databases/` directory
- Check for required files
- Verify imports

## Running the Application
To start the CMS:

```bash
python run.py
```
