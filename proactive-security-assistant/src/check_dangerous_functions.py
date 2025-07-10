# proactive-security-assistant/src/check_dangerous_functions.py
import os

# Map file extensions to their corresponding language configuration key.
# This should match the keys in the 'dangerous_functions' section of the config.
LANGUAGE_MAPPING = {
    '.py': 'python',
    '.js': 'javascript',
    '.jsx': 'javascript',
    '.ts': 'javascript',
    '.tsx': 'javascript',
    '.php': 'php',
    '.go': 'go',
}

# Directories to ignore during scanning
IGNORED_DIRS = ['.git', 'node_modules', 'vendor', 'dist', 'build', '__pycache__']

def find_dangerous_functions(repo_path, config):
    """
    Scans code for usage of functions marked as dangerous in the config.

    Args:
        repo_path (str): The root directory of the repository to scan.
        config (dict): The configuration containing the 'dangerous_functions' key.

    Returns:
        list: A list of dictionaries, each representing a finding.
    """
    findings = []
    dangerous_functions_config = config.get('dangerous_functions', {})
    if not dangerous_functions_config:
        return findings

    for root, dirs, files in os.walk(repo_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for filename in files:
            file_ext = os.path.splitext(filename)[1]
            language = LANGUAGE_MAPPING.get(file_ext)

            if not language:
                continue

            functions_to_check = dangerous_functions_config.get(language, [])
            if not functions_to_check:
                continue

            file_path = os.path.join(root, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for func in functions_to_check:
                            # This is a simple text search. For more advanced analysis,
                            # AST parsing could be considered.
                            # This check looks for patterns like 'eval(' or 'eval ('.
                            # Using a simple word boundary check to avoid matching substrings.
                            # e.g., don't match 'my_exec_function' if 'exec' is the target.
                            # This is still a basic check and could be improved with AST parsing.
                            import re
                            if re.search(r'\b' + re.escape(func) + r'\b', line):
                                findings.append({
                                    'file': os.path.relpath(file_path, repo_path),
                                    'line': line_num,
                                    'function': func
                                })
                                # Found a function on this line, no need to check for others.
                                break
            except Exception:
                # This can happen for binary files or files with encoding issues.
                pass

    return findings