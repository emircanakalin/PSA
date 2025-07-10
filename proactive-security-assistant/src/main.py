# proactive-security-assistant/src/main.py
import yaml
import os
import sys

from check_sensitive_data import find_sensitive_data
from check_licenses import check_project_licenses
from check_iac import scan_iac_files
from check_dangerous_functions import find_dangerous_functions

def load_config(config_path):
    """Loads the configuration file from the specified path."""
    if not os.path.exists(config_path):
        print(f"⚠️ Warning: Configuration file not found at '{config_path}'. Using default empty settings.")
        return {}
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"❌ Error: Could not parse the configuration file: {e}")
        sys.exit(1)

def run_sensitive_data_scan(repo_path, config):
    """Runs the sensitive data scan and prints findings."""
    print("\n[1/4] 🔍 Starting Sensitive Data Scan...")
    patterns = config.get('sensitive_data_patterns', [])
    findings = find_sensitive_data(repo_path, patterns)
    if findings:
        print("  🚨 SENSITIVE DATA FINDINGS:")
        for finding in findings:
            print(f"    - File: {finding['file']}:{finding['line']} | Rule: {finding['rule']}")
        return True
    print("  ✅ Sensitive data scan clean.")
    return False

def run_license_scan(repo_path, config):
    """Runs the license compliance scan and prints findings."""
    print("\n[2/4] ⚖️ Starting License Compliance Scan...")
    allowed = config.get('allowed_licenses', [])
    findings = check_project_licenses(repo_path, allowed)
    if findings:
        print("  🚫 LICENSE COMPLIANCE ISSUES:")
        for finding in findings:
            print(f"    - Package: {finding['package']} | License: {finding['license']} (Not in allowlist)")
        return True
    print("  ✅ License compliance scan clean.")
    return False

def run_iac_scan(repo_path):
    """Runs the IaC security scan and prints findings."""
    print("\n[3/4] 🏗️ Starting IaC Security Scan...")
    findings = scan_iac_files(repo_path)
    if findings:
        print("  🏗️ IAC SECURITY ISSUES:")
        for finding in findings:
            print(f"    - File: {finding['file_path']}:{finding.get('line_number', 'N/A')}")
            print(f"      Resource: {finding['resource']}")
            print(f"      Rule: {finding['check_id']} ({finding['check_name']})")
        return True
    print("  ✅ IaC security scan clean.")
    return False

def run_dangerous_function_scan(repo_path, config):
    """Runs the dangerous function scan and prints warnings."""
    print("\n[4/4] ☢️ Starting Dangerous Function Scan...")
    findings = find_dangerous_functions(repo_path, config)
    if findings:
        print("  ⚠️ DANGEROUS FUNCTION USAGE WARNINGS (does not fail build):")
        print("    The following uses may pose a security risk and require manual review:")
        for finding in findings:
            print(f"    - File: {finding['file']}:{finding['line']} | Function: `{finding['function']}`")
    else:
        print("  ✅ Dangerous function scan clean.")
    # This scan is informational, so it never fails the build.
    return False

def main():
    """Main scanning function."""
    # Get inputs from environment variables, which are set by the GitHub Action.
    # Provide sensible defaults for local execution.
    repo_path = os.getenv('INPUT_REPO_PATH', '.')
    config_path = os.getenv('INPUT_CONFIG_PATH', '.github/security-config.yml')

    # For local runs, if the default config is not in .github/, check the root.
    if not os.path.exists(config_path) and config_path.endswith('.github/security-config.yml'):
        root_config = os.path.join(os.path.dirname(repo_path), 'security-config.yml')
        if os.path.exists(root_config):
            config_path = root_config

    print("=================================================")
    print("= Proactive Security and Compliance Assistant   =")
    print("=================================================")
    print(f"Scanning Directory: {repo_path}")
    print(f"Using Configuration File: {config_path}")

    config = load_config(config_path)
    
    # Each function returns True if it finds issues that should fail the build.
    issue_found_flags = [
        run_sensitive_data_scan(repo_path, config),
        run_license_scan(repo_path, config),
        run_iac_scan(repo_path),
        run_dangerous_function_scan(repo_path, config) # Always returns False
    ]

    print("\n-------------------")
    print("Scan complete.")
    
    if any(issue_found_flags):
        print("\n❌ Security or compliance issues were detected. Failing the build.")
        sys.exit(1)
    else:
        print("\n✅ No critical issues found. Build successful.")
        sys.exit(0)

if __name__ == "__main__":
    main()