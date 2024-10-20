# Author: Ujwal N K
# Created On:
# Check for any import statements in the user-code

import re

def check_imports(path: str):
    """
    Function check the imported modules in a python file
    
    @param:
        path: str - File path to check

    @return:
        modules_imported: list - List of modules imported

    """

    modules_imported = []

    with open(path, 'r') as file:
        content = file.read()

    # Regular expressions for different types of imports
    import_re = re.compile(r'^\s*import\s+(\w+)', re.MULTILINE)
    from_import_re = re.compile(r'^\s*from\s+(\w+)', re.MULTILINE)

    # Find all matches
    import_matches = import_re.findall(content)
    from_import_matches = from_import_re.findall(content)

    # Combine and deduplicate the results
    modules_imported = list(set(import_matches + from_import_matches))

    return modules_imported