import yaml
import sys

try:
    with open('docker-compose.yml', 'r') as f:
        yaml.safe_load(f)
    print("YAML is valid")
except Exception as e:
    print(f"YAML error: {e}")
    sys.exit(1)
