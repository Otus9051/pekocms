# Architecture Overview

PekoCMS is built as a modular desktop application using **Python** and **PySide6 (Qt)**. It runs completely offline with a local SQLite database architecture.

## Core Components

### 1. Main Application (`app/pyside_app.py`)
The central controller and view manager.
- **MainWindow**: Manages the main window lifecycle, layout, and global events.
- **Mode System**: Switches between `Pathology` (Lab) and `Polyclinic` (Doctor/OPD) interfaces using a `QStackedWidget`.
- **Responsive Layout**: Uses dynamic resizing and tabbed interfaces to adapt to different screen sizes.

### 2. Reporting Engine (`app/pdf_generator.py`)
Handles the generation of PDF documents using `fpdf2`.
- **Invoices**: Generates billing receipts with tax calculations.
- **Lab Reports**: Creates formatted test results with header/footer branding.

### 3. Background Workers (`app/threads.py`)
To keep the UI responsive, heavy operations are offloaded to background threads (`QThread`).
- **CatalogueLoader**: Loads test catalogues.
- **Database Workers**: Handles complex queries to prevent UI freezing.

### 4. Configuration (`app/branding.py`)
Loads settings from `config.yaml` and exposes them as application-wide constants. This separates configuration from logic.

---

## Database Architecture (`app/db/`)

PekoCMS uses a multi-file SQLite approach for modularity and easier backup/maintenance.

| Module | File | Purpose |
|O---|---|---|
| `auth_db.py` | `users.db` | User authentication and role management (Admin/User). |
| `catalogue_db.py` | `catalogue.db` | Master list of all pathology tests and prices. |
| `patient_cms_db.py` | `patient_cms.db` | Core patient records and visit history. |
| `polyclinic_db.py` | `polyclinic.db` | Doctor profiles, appointments, and OPD queues. |
| `special_tests_db.py` | `catalogue.db` | Custom/User-defined tests added significantly. |
| `invoice_service.py` | `datasheet.db` | Financial records and daily collections. |

---

## Efficiency Optimizations

We have implemented several tweaks to ensure PekoCMS runs smoothly even on lower-end hardware:

### 1. On-Demand SQL Search
**Problem**: Loading 1000+ tests into the UI memory slowed down startup and search.
**Solution**: The "Add Test" search bar now queries the SQLite database directly using SQL `LIKE` clauses only when the user types. This keeps memory usage low and results instant.

### 2. Batch UI Updates
**Problem**: Inserting hundreds of rows into a table freezes the UI.
**Solution**: We explicitly disable UI updates (`setUpdatesEnabled(False)`) before bulk insertions and re-enable them after. This reduces rendering time by ~90%.

### 3. Background Threading
**Problem**: Database initialization and catalogue refreshing locked the main window.
**Solution**: All heavy data lifting happens in `QThread` workers (defined in `threads.py`), allowing the UI to remain interactive (showing spinners/progress bars) during loads.

### 4. Lazy Loading
**Problem**: The "Polyclinic" tab has heavy doctor/booking data.
**Solution**: This data is not loaded until the user actually clicks the Polyclinic tab, speeding up the initial application launch.

### 5. Local Caching
**Problem**: Frequently accessed small datasets (like "Special Tests") required repeated DB hits.
**Solution**: These are preloaded into memory (`self.special_tests_cache`) on startup for instant access without disk I/O.
