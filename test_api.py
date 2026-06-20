import requests

# Test the send verification code endpoint
url = "http://127.0.0.1:8080/api/users/phone/send-code/"
# OR if your Django is running on a different port:
# url = "http://127.0.0.1:8000/api/users/phone/send-code/"

data = {
    "phone_number": "07030673089",
    "platform": "ole"
}

try:
    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
except Exception as e:
    print(f"Error: {e}")