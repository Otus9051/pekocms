# Configuration Guide

PekoCMS uses a `config.yaml` file for easy customization of branding, assets, and application behavior. This allows you to adapt the system for different clinics without touching the code.

## File Structure: `config.yaml`

The configuration file is located at the root of the project.

### Branding
Control the names and contact details displayed throughout the app and on generated reports.

```yaml
APP_NAME: "PekoCMS"                  # Application window title
CLINIC_NAME: "Peko Polyclinic"       # Display name in UI
CLINIC_NAME_FORMAL: "Peko Polyclinic Pvt Ltd" # Used in official reports/invoices
CLINIC_ADDRESS: "123 Health Street, Wellness City"
CLINIC_CONTACT: "+1 (555)-0199"
FOOTER_TEXT: "Powered by PekoCMS"    # Bottom app bar text
PATIENT_ID_PREFIX: "PEK"             # Prefix for auto-generated IDs (e.g., PEK1001)
```

### Assets
Paths to branding images. Files should be placed in the `assets/` directory.

```yaml
LOGO_SVG: "logo.svg"                 # Scalable logo for UI headers
LOGO_PNG: "logo_print.png"           # High-res logo for PDF reports
```

### Reporting
Settings for generated PDFs.

```yaml
REPORT_DELIVERY_TIMES: "Reports available: 12 PM - 2 PM & 5 PM - 8 PM"
```

### Theme
Customize the application color scheme.

```yaml
THEME_PRIMARY: "#0078D4"             # Main brand color (Buttons, Headers)
THEME_DANGER: "#D32F2F"              # Error/Warning actions (Delete, Shutdown)
```
