# proactive-security-assistant/src/check_iac.py
import subprocess
import json
import os

def scan_iac_files(repo_path):
    """
    Scans Infrastructure as Code (IaC) files using checkov.

    Args:
        repo_path (str): The root directory of the repository to scan.

    Returns:
        list: A list of dictionaries, each representing a finding.
    """
    findings = []
    
    # Check if the directory to be scanned exists
    if not os.path.isdir(repo_path):
        print(f"Warning: IaC scan directory not found: {repo_path}")
        return findings

    print(f"  -> Scanning directory '{repo_path}' with checkov...")
    
    try:
        # Run checkov and get the output in JSON format
        # --quiet flag prevents successful checks from appearing in the output.
        # --soft-fail flag ensures the exit code is 0 even if issues are found, allowing us to control the flow.
        result = subprocess.run(
            [
                'checkov',
                '--directory', repo_path,
                '--output', 'json',
                '--quiet',
                '--soft-fail' 
            ],
            capture_output=True,
            text=True,
            check=False # We check the status code manually
        )

        # checkov can return 0 even if there's an error, so we check stderr
        # checkov may return a non-zero exit code even on success if findings are present,
        # so we primarily check for content in stdout.
        if not result.stdout.strip():
            if result.returncode != 0:
                print(f"  - Warning: checkov command may have failed (exit code {result.returncode}).")
                print(f"    Stderr: {result.stderr}")
            # No output means no failed checks found.
            return findings

        report = json.loads(result.stdout)
        
        # The report can be a list (for multiple frameworks) or a dict (for one).
        reports = report if isinstance(report, list) else [report]

        for rep in reports:
            if isinstance(rep, dict) and rep.get('results'):
                failed_checks = rep['results'].get('failed_checks', [])
                for check in failed_checks:
                    findings.append({
                        'check_id': check.get('check_id'),
                        'check_name': check.get('check_name'),
                        'file_path': check.get('file_path'),
                        'line_number': check.get('file_line_range', [None, None])[0],
                        'resource': check.get('resource')
                    })

    except FileNotFoundError:
        print("  - Error: 'checkov' command not found. Please ensure checkov is installed.")
    except json.JSONDecodeError:
        print("  - Error: Failed to decode checkov output as JSON. Raw output:")
        print(f"    {result.stdout}")
    except Exception as e:
        print(f"  - An unexpected error occurred during IaC scan: {e}")

    return findings