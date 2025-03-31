import os
import json

def load_options_set(file_path):
    """Load the options.set file and extract the list of active mods."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    mod_list = []
    in_mod_section = False
    for line in lines:
        line = line.strip()
        if "{options" in line:
            in_mod_section = False
        if "{mods" in line:
            in_mod_section = True
        elif in_mod_section:
            if "}" in line:
                break
            if line.startswith("\"mod_"):
                mod_id = line.split('_')[1].split(':')[0].strip('"')
                mod_list.append(mod_id)
    
    return mod_list

def scan_mods_folder(folder_path):
    """Scan the mods folder and retrieve their names and IDs."""
    mods = {}
    
    if not os.path.exists(folder_path):
        return mods
        
    for mod_id in os.listdir(folder_path):
        mod_path = os.path.join(folder_path, mod_id)
        if not os.path.isdir(mod_path):
            continue
            
        mod_info_path = os.path.join(mod_path, "mod.info")
        if os.path.isfile(mod_info_path):
            with open(mod_info_path, "r", encoding="utf-8") as f:
                for line in f:
                    if "{name" in line:
                        mod_name = line.split('"')[1]
                        mods[mod_id] = mod_name
                        break
    
    return mods

def save_config(config_path, data):
    """Save the user's configuration (file paths)."""
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_config(config_path):
    """Load the configuration if it exists."""
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def update_mods_section(options_set_path, active_mods):
    """
    Update only the {mods} section of the options.set file
    without modifying the rest of the file.
    """
    with open(options_set_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Find the start and end of the {mods} section
    start_index = None
    end_index = None
    in_mods_section = False
    
    for i, line in enumerate(lines):
        if "{mods" in line:
            start_index = i
            in_mods_section = True
        elif in_mods_section and "}" in line:
            end_index = i
            break
    
    # Create the new {mods} section
    new_mods_lines = ["\t{mods\n"]
    for mod_id in active_mods:
        new_mods_lines.append(f'\t\t"mod_{mod_id}:0"\n')
    new_mods_lines.append("\t}\n")
    
    # If the {mods} section exists, replace it
    if start_index is not None and end_index is not None:
        new_lines = lines[:start_index] + new_mods_lines + lines[end_index+1:]
        
        with open(options_set_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        return True
    
    # If the {mods} section doesn't exist, add it before the last brace of the main options section
    else:
        # Find the closing brace of the options section
        options_end_index = None
        options_brace_count = 0
        in_options_section = False
        
        for i, line in enumerate(lines):
            line_stripped = line.strip()
            if line_stripped == "{options":
                in_options_section = True
                options_brace_count += 1
            elif in_options_section:
                if "{" in line_stripped:
                    options_brace_count += line_stripped.count("{")
                if "}" in line_stripped:
                    options_brace_count -= line_stripped.count("}")
                    if options_brace_count == 0:
                        options_end_index = i
                        break
        
        if options_end_index is not None:
            # Insert before the closing brace of options
            new_lines = lines[:options_end_index] + new_mods_lines + lines[options_end_index:]
            
            with open(options_set_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        
        return False

def save_preset(config_path, preset_name, active_mods):
    """Save a preset configuration of mods."""
    config = load_config(config_path)
    
    # Initialize presets if they don't exist
    if "presets" not in config:
        config["presets"] = {}
    
    # Save the preset
    config["presets"][preset_name] = active_mods
    save_config(config_path, config)
    return True

def load_preset(config_path, preset_name):
    """Load a preset configuration of mods."""
    config = load_config(config_path)
    
    if "presets" not in config or preset_name not in config["presets"]:
        return None
    
    return config["presets"][preset_name]

def delete_preset(config_path, preset_name):
    """Delete a preset configuration."""
    config = load_config(config_path)
    
    if "presets" not in config or preset_name not in config["presets"]:
        return False
    
    del config["presets"][preset_name]
    save_config(config_path, config)
    return True

def get_all_presets(config_path):
    """Get all preset names."""
    config = load_config(config_path)
    
    if "presets" not in config:
        return []
    
    return list(config["presets"].keys())

def get_config_path():
    """Get the path where the configuration file should be stored"""
    # Determine appropriate config directory based on OS
    if os.name == 'nt':  # Windows
        app_data = os.path.join(os.environ['APPDATA'], "GoH Mod Manager")
    else:  # Linux/Mac
        app_data = os.path.join(os.path.expanduser("~"), ".gohmodmanager")
    
    # Create directory if it doesn't exist
    if not os.path.exists(app_data):
        os.makedirs(app_data)
    
    return os.path.join(app_data, "config.json")