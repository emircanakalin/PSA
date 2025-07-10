# proactive-security-assistant/src/check_licenses.py
import os
import subprocess
import json
import re

def check_python_licenses(repo_path, allowed_licenses):
    """Checks Python dependency licenses using requirements.txt."""
    findings = []
    req_file = os.path.join(repo_path, 'requirements.txt')
    
    if not os.path.exists(req_file):
        return findings

    try:
        # First, read the target repository's requirements to know what to check.
        target_packages = set()
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Handle editable installs from git with #egg=
                if '#egg=' in line:
                    line = line.split('#egg=')[-1]
                
                # Remove version specifiers, extras, and other markers to get the clean package name.
                # This handles cases like: requests[security]==2.25.1 -> requests
                clean_line = line.split('==')[0].split('>=')[0].split('<=')[0].split('>')[0].split('<')[0].split('[')[0].split('~=')[0].strip()
                
                # Ignore lines that are just flags like '-e' after processing
                if clean_line and not clean_line.startswith('-'):
                    target_packages.add(clean_line)

        # Get licenses in JSON format using pip-licenses
        # Using a public PyPI URL is more reliable in CI environments
        result = subprocess.run(
            ['pip-licenses', '--format=json', '--pypi-url=https://pypi.org/pypi'],
            capture_output=True, text=True, check=True, cwd=repo_path
        )
        dependencies = json.loads(result.stdout)
        
        for dep in dependencies:
            package_name = dep.get('Name')
            # Only check packages that are in the target's requirements.txt
            if package_name and package_name.lower() in (p.lower() for p in target_packages):
                license_str = dep.get('License', 'Unknown')
                # Use regex to check if any allowed license is present as a whole word in the license string.
                # This is more robust for SPDX expressions like "(MIT OR Apache-2.0)".
                # The \b ensures whole word matching to avoid matching 'ISC' in 'MISC'.
                is_allowed = any(re.search(r'\b' + re.escape(l) + r'\b', license_str, re.IGNORECASE) for l in allowed_licenses)

                if not is_allowed:
                    findings.append({
                        'type': 'python',
                        'package': package_name,
                        'version': dep.get('Version'),
                        'license': license_str
                    })

    except FileNotFoundError:
        print("  - Warning: 'pip-licenses' command not found. Skipping Python license check.")
    except subprocess.CalledProcessError as e:
        print(f"  - Warning: Error while checking Python licenses. Is 'pip install -r requirements.txt' complete?")
        print(f"    {e.stderr}")
    
    return findings

def check_npm_licenses(repo_path, allowed_licenses):
    """Checks NPM dependency licenses using package.json."""
    findings = []
    package_json_file = os.path.join(repo_path, 'package.json')
    node_modules_dir = os.path.join(repo_path, 'node_modules')

    if not os.path.exists(package_json_file):
        return findings

    if not os.path.isdir(node_modules_dir):
        print("Warning: 'package.json' found but 'node_modules' directory is missing. Skipping NPM license check.")
        print("Hint: Make sure to run 'npm install' before this scan.")
        return findings

    try:
        # Get licenses in JSON format using license-checker-js
        result = subprocess.run(
            ['license-checker-js', '--json'],
            capture_output=True, text=True, check=True, cwd=repo_path
        )
        dependencies = json.loads(result.stdout)

        for package_name, dep_info in dependencies.items():
            license_str = dep_info.get('licenses', 'Unknown')
            
            # Use the same robust regex check for NPM packages.
            is_allowed = any(re.search(r'\b' + re.escape(l) + r'\b', license_str, re.IGNORECASE) for l in allowed_licenses)

            if not is_allowed:
                findings.append({
                    'type': 'npm',
                    'package': package_name,
                    'license': license_str
                })

    except FileNotFoundError:
        print("  - Warning: 'license-checker-js' command not found. Skipping NPM license check.")
    except subprocess.CalledProcessError as e:
        print(f"  - Warning: Error while checking NPM licenses. Is 'npm install' complete?")
        print(f"    {e.stderr}")

    return findings

def check_project_licenses(repo_path, allowed_licenses):
    """Checks licenses for all dependencies in the project."""
    if not allowed_licenses:
        print("  - Info: Allowlist for licenses is empty, skipping license check.")
        return []
        
    all_findings = []
    if os.path.exists(os.path.join(repo_path, 'requirements.txt')):
        print("  -> Checking Python (requirements.txt) licenses...")
        all_findings.extend(check_python_licenses(repo_path, allowed_licenses))
    
    if os.path.exists(os.path.join(repo_path, 'package.json')):
        print("  -> Checking NPM (package.json) licenses...")
        all_findings.extend(check_npm_licenses(repo_path, allowed_licenses))
    
    return all_findings