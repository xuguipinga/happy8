import requests
import datetime

def test_statistics():
    base_url = "http://127.0.0.1:5000/api/statistics/purchases"
    
    # 1. 模拟查询今天的数据 (假设今天有数据，或者无数据)
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(f"Testing with date: {today}")
    
    # Login first? No, use hardcoded tenant_id if possible or mock auth?
    # The API requires auth. I need a token.
    # Alternatively, I can disable require_auth temporarily or use a known token.
    # Since I cannot easily get a token, I will check the code logic directly.
    # Wait, I can try to login if I know the credentials.
    # user: admin, pass: 123456 (often used default)
    
    session = requests.Session()
    try:
        login_res = session.post("http://127.0.0.1:5000/api/auth/login", json={
            "username": "admin",
            "password": "password123" # Taking a guess, or check seeder
        })
        if login_res.status_code == 200:
            token = login_res.json()['data']['token']
            headers = {"Authorization": f"Bearer {token}"}
        else:
            print("Login failed, trying without auth (might fail)")
            headers = {}
    except:
        print("Login failed")
        headers = {}

    params = {
        "start_date": today,
        "end_date": today,
        "period": "day"
    }
    
    try:
        res = session.get(base_url, params=params, headers=headers)
        print(f"Response Code: {res.status_code}")
        print(f"Response Data: {res.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_statistics()
