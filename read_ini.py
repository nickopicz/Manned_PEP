def parse_ini(ini_path):
    with open(ini_path, 'r') as file:
        lines = file.readlines()

    alias_to_index = {}
    current_section = None
    for line in lines:
        line = line.strip()
        # Get section name
        if line.startswith('Par') and 'Alias' in line:
            parts = line.split('=')
            key = parts[0].strip()
            value = parts[1].strip().replace('"', '')  # Removing quotes
            if 'Alias' in key:
                param_num = key.split()[1]
                alias_name = value
                index_key = f"Par {param_num} Index"
                for search_line in lines:
                    if search_line.startswith(index_key):
                        index_value = int(search_line.split('=')[1].strip())
                        alias_to_index[alias_name] = index_value
                        break

    return alias_to_index


# Sample usage
alias_to_index_mapping = parse_ini('ACS_NoCoNi.ini')
print(alias_to_index_mapping)
