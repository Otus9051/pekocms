# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for PekoCMS (PySide6 Desktop App)
Build with: pyinstaller pyside_app.spec
"""

block_cipher = None

a = Analysis(
    ['app/pyside_app.py'],
    pathex=['app', 'db'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
    ],
    hiddenimports=[
        'PySide6',
        'db.auth_db',
        'db.patient_cms_db',
        'db.datasheet_db',
        'db.report_tracker_db',
        'db.invoice_service',
        'db.data_fetcher',
        'db.catalogue_db',
        'db.special_tests_db',
        'db.polyclinic_db',
        'app.pdf_generator',
        'app.branding',
        'app.theme',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PekoCMS',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets\\icon.ico',
)

# Create separate executable for migration tool
migration_a = Analysis(
    ['migration_tool.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('databases', 'databases'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

migration_pyz = PYZ(migration_a.pure, migration_a.zipped_data, cipher=block_cipher)

migration_exe = EXE(
    migration_pyz,
    migration_a.scripts,
    migration_a.binaries,
    migration_a.datas,
    [],
    name='MigrationTool',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Console for migration tool
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
