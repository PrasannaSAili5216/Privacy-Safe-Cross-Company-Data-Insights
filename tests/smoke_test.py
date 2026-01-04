import requests
import time
import sys

def test_server_is_running(url="http://localhost:8501", timeout=5):
    """
    Smoke test to verify the Streamlit server is up and responding.
    """
    print(f"Testing connection to {url}...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✅ Server is UP! (Status: {response.status_code})")
                return True
            else:
                print(f"⚠️ Server responded with status: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("⏳ Connection refused... waiting for server to start...")
            time.sleep(1)
            
    print("❌ Failed to connect to server after timeout.")
    return False

if __name__ == "__main__":
    success = test_server_is_running(timeout=10)
    if not success:
        sys.exit(1)
