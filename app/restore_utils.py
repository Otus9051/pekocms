
def restore_system_from_backup(zip_path, parent_window, on_success_callback=None):
    """
    Restore the system (DBs, Config, Logos) from a ZIP backup.
    WARNING: Overwrites existing data.
    """
    import zipfile
    import shutil
    import os
    import yaml
    from PySide6 import QtWidgets
    from app.utils import get_database_dir, get_config_path, get_asset_path
    
    try:
        if not zipfile.is_zipfile(zip_path):
            raise ValueError("Selected file is not a valid ZIP archive.")
            
        db_dir = get_database_dir()
        conf_path = get_config_path()
        assets_dir = os.path.dirname(get_asset_path("dummy")) # Get assets dir
        
        # Confirmation
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle("Confirm Restore")
        msg.setText("Are you sure you want to restore from this backup?")
        msg.setInformativeText("This will OVERWRITE all current data (Patients, Tests, Settings). This action cannot be undone.\n\nThe application will need to restart.")
        msg.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Cancel)
        
        if msg.exec() != QtWidgets.QMessageBox.Yes:
            return False

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # list files
            files = zip_ref.namelist()
            
            # Simple validation
            has_db = any(f.endswith('.db') for f in files)
            if not has_db:
                QtWidgets.QMessageBox.warning(parent_window, "Invalid Backup", "The backup does not contain any database files.")
                return False

            # 1. Restore Databases
            for file in files:
                if file.endswith('.db') and '/' not in file: # Root level dbs
                    zip_ref.extract(file, db_dir)
            
            # 2. Restore Config
            if "config.yaml" in files:
                # Backup current config just in case? No, "Overwrite" implies risk.
                with open(conf_path, 'wb') as f:
                    f.write(zip_ref.read("config.yaml"))
                    
            # 3. Restore Logos
            # Look for logos/ folder in zip
            logo_files = [f for f in files if f.startswith('logos/') and not f.endswith('/')]
            if logo_files:
                # Ensure we have a place to put them. 
                # We put them in assets/restored_logos to separate them? 
                # Or just root assets? Let's use assets/custom
                target_logo_dir = os.path.join(assets_dir, "custom")
                os.makedirs(target_logo_dir, exist_ok=True)
                
                restored_logos_map = {} # old_name -> new_absolute_path
                
                for logof in logo_files:
                    filename = os.path.basename(logof)
                    target_path = os.path.join(target_logo_dir, filename)
                    with open(target_path, 'wb') as f:
                        f.write(zip_ref.read(logof))
                    restored_logos_map[filename] = target_path
                
                # Update config to point to new logo paths if necessary
                # We need to read the config we just restored
                if os.path.exists(conf_path):
                    try:
                        with open(conf_path, 'r', encoding='utf-8') as f:
                            config = yaml.safe_load(f) or {}
                        
                        updated = False
                        if 'BRANDING_LOGO' in config:
                            base = os.path.basename(config['BRANDING_LOGO'])
                            if base in restored_logos_map:
                                config['BRANDING_LOGO'] = restored_logos_map[base]
                                updated = True
                                
                        if 'REPORT_LOGO' in config:
                            base = os.path.basename(config['REPORT_LOGO'])
                            if base in restored_logos_map:
                                config['REPORT_LOGO'] = restored_logos_map[base]
                                updated = True
                        
                        if updated:
                            with open(conf_path, 'w', encoding='utf-8') as f:
                                yaml.dump(config, f)
                    except Exception as e:
                        print(f"Error updating config paths: {e}")

        QtWidgets.QMessageBox.information(parent_window, "Restore Complete", "System restored successfully.\n\nThe application will now close. Please restart it.")
        
        if on_success_callback:
            on_success_callback()
            
        return True
        
    except Exception as e:
        QtWidgets.QMessageBox.critical(parent_window, "Restore Failed", f"An error occurred:\n{str(e)}")
        return False
