
import requests

BASE = "http://127.0.0.1:8000"
results = []

def check(name, method, url, **kwargs):
    try:
        r = requests.request(method, url, **kwargs)
        status = "✅ PASS" if r.status_code in [200, 201] else f"❌ FAIL ({r.status_code})"
        print(f"{status} | {name} | {r.text[:80]}")
    except Exception as e:
        print(f"❌ ERROR | {name} | {e}")

# Health
check("Root", "GET", f"{BASE}/")
check("Health", "GET", f"{BASE}/health")

# Auth
check("Register", "POST", f"{BASE}/api/auth/register",
      json={"username": "testuser2", "email": "test2@test.com", "password": "test123"})

login = requests.post(f"{BASE}/api/auth/login",
                      json={"username": "testuser2", "password": "test123"})
token = login.json().get("access_token", "")
print(f"\n🔑 Token: {token[:30]}...\n" if token else "❌ Login Failed!\n")

headers = {"Authorization": f"Bearer {token}"}

# Protected routes
check("Get Me",       "GET",  f"{BASE}/api/auth/me",          headers=headers)
check("Chat Send",    "POST", f"{BASE}/api/chat/send",        headers=headers,
      json={"message": "I feel stressed"})
check("Mood Log",     "POST", f"{BASE}/api/mood/log",         headers=headers,
      json={"mood_level": 3, "note": "test"})
check("Mood History", "GET",  f"{BASE}/api/mood/history",     headers=headers)
check("Dashboard",    "GET",  f"{BASE}/api/dashboard",        headers=headers)