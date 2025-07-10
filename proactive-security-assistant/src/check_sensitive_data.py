# proactive-security-assistant/src/check_sensitive_data.py
import os
import re

# Directories and file extensions to ignore during scanning.
# This list can be expanded.
IGNORED_DIRS = ['.git', 'node_modules', 'vendor', 'dist', 'build', '__pycache__', '.venv', 'env']
IGNORED_EXTENSIONS = [
    # Common binary and non-source files
    '.log', '.lock', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp',
    '.eot', '.ttf', '.woff', '.woff2', '.css',
    # Minified files
    '.min.js',
]

def find_sensitive_data(repo_path, patterns):
    """
    Scans files in the specified path for sensitive data patterns.

    Args:
        repo_path (str): The root directory of the repository to scan.
        patterns (list): A list of regex patterns to search for.

    Returns:
        list: A list of dictionaries, each representing a finding.
              Example: [{'file': 'path/to/file', 'line': 12, 'rule': 'pattern'}]
    """
    findings = []
    if not patterns:
        return findings

    compiled_patterns = []
    for pattern in patterns:
        try:
            compiled_patterns.append((pattern, re.compile(pattern)))
        except re.error as e:
            print(f"Warning: Invalid regex pattern '{pattern}' skipped: {e}")

    for root, dirs, files in os.walk(repo_path, topdown=True):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]

        for filename in files:
            # Skip ignored file extensions
            if any(filename.endswith(ext) for ext in IGNORED_EXTENSIONS):
                continue

            file_path = os.path.join(root, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for original_pattern, compiled_pattern in compiled_patterns:
                            if compiled_pattern.search(line):
                                findings.append({
                                    'file': os.path.relpath(file_path, repo_path),
                                    'line': line_num,
                                    'rule': original_pattern
                                })
                                # Once a rule is found on a line, we can stop checking other rules for that line.
                                break 
            except UnicodeDecodeError:
                # This is common for binary files, so we can safely ignore it.
                pass
            except Exception as e:
                # Log other unexpected errors for debugging.
                print(f"  - Warning: Could not read file {file_path}: {e}")
                pass

    return findings