# Building PekoCMS

This guide explains how to build the executable and installer for PekoCMS.

## Build Requirements
- `pyinstaller` (installed via requirements.txt)
- Inno Setup Compiler (for creating the Windows installer)

## Building the Executable
We use PyInstaller to build the standalone executable.

1.  **Build the application:**
    ```bash
    pyinstaller pyside_app.spec
    ```
    This will create the executable in the `dist/` directory.

2.  **Build the sync worker (if separate):**
    ```bash
    pyinstaller sync_worker.spec
    ```

## Creating the Installer
We use Inno Setup to create a distributing installer (`.exe`).

1.  Install **Inno Setup**.
2.  Open `setup.iss` with Inno Setup Compiler.
3.  Compile the script.
4.  The output installer will be generated (check the output path configuration in `setup.iss`).

## Manual Build Verification
After building:
1.  Navigate to `dist/PekoCMS`.
2.  Run `PekoCMS.exe`.
3.  Verify the application launches and loads assets correctly.
