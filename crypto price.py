import requests
# This hides a warning message about bypassing security checks
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print("🌐 ATTEMPTING NETWORK CONNECTION (BYPASSING SSL)...")

try:
    # Test 1: Let's try an incredibly simple IP API link instead
    url = "https://api.ipify.org?format=json"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    # verify=False tells Python: "Trust this website link without a security check"
    response = requests.get(url, headers=headers, verify=False, timeout=5)
    
    data = response.json()
    print(f"\n✅ SUCCESS! Your public network IP data is: {data}")

except Exception as e:
    print(f"\n❌ Technical Error Message: {e}")