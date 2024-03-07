import re
global_env = {}

def parse_oen_code(code):
    # Regular expressions for matching OEN code patterns
    variable_pattern = re.compile(r'(\w+)\s*=\s*{(.+?)}', re.DOTALL)
    config_pattern = re.compile(r'(\w+)\s*=\s*{\s*\.(\w+)\s*}', re.DOTALL)
    export_pattern = re.compile(r'export\s+(\w+)') # Capture exported variable name
    import_pattern = re.compile(r'import\s+\"(\w+\.on)\"') # Capture imported file name

    parsed_data = {}

    # Find variable assignments
    variables = variable_pattern.findall(code)
    for var_name, var_content in variables:
        parsed_data[var_name] = parse_key_value_pairs(var_content)

    # Find configurations
    configs = config_pattern.findall(code)
    for config_name, included_keys in configs:
        parsed_data[config_name] = {'include': included_keys}

    # Resolve included keys
    resolve_includes(parsed_data)

    # Handle exports
    exports = export_pattern.findall(code)
    for exported_var in exports:
        if exported_var in parsed_data:
            global_env[exported_var] = parsed_data[exported_var]

    # Handle imports
    imports = import_pattern.findall(code)
    for imported_file in imports:
        with open(imported_file) as import_file:
            import_code = import_file.read()
            import_data = parse_oen_code(import_code)
            parsed_data.update(import_data)

    return parsed_data

def parse_key_value_pairs(content):
    # Parse key-value pairs inside { }
    key_value_pairs = re.findall(r'(\w+)\s*:\s*([\w\d]+)', content)
    parsed_pairs = {key: int(value) if value.isdigit() else value for key, value in key_value_pairs}
    return parsed_pairs


def resolve_includes(parsed_data):
    for key, value in parsed_data.items():
        if isinstance(value, dict) and 'include' in value:
            included_keys = value['include'].split(',')

            # Filter keys from parsed_data and global_env
            included_data = {}
            for k in included_keys:
                if k in parsed_data:
                    included_data[k] = parsed_data[k]
                elif k in global_env:
                    included_data[k] = global_env[k]
                else:
                    # Handle missing keys here
                    print(f"Warning: Key '{k}' not found in parsed_data or global_env.")

            # Update the parsed_data with the resolved included_data
            parsed_data[key] = included_data



# Read OEN code from the file
with open("example.on") as f:
    code = f.read()

# Parse OEN code
parsed = parse_oen_code(code)

print(parsed)
