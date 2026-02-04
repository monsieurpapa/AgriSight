import os
import sys
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agrisight.settings')
django.setup()

# Import new modules to check for syntax errors
try:
    from apps.sentinel_hub.batch_client import BatchClient
    print("[PASS] Imported BatchClient")
except Exception as e:
    print(f"[FAIL] BatchClient import: {e}")

try:
    from apps.satellite_processing.models import BatchJob
    print("[PASS] Imported BatchJob model")
except Exception as e:
    print(f"[FAIL] BatchJob model import: {e}")

try:
    from apps.satellite_processing.tasks import trigger_batch_processing, monitor_batch_jobs
    print("[PASS] Imported tasks")
except Exception as e:
    print(f"[FAIL] Tasks import: {e}")

print("Verification complete.")
