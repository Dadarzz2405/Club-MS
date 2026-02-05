import requests
from requests.auth import HTTPBasicAuth

API_KEY = "48d2d2c2c6965381b388b236fe83345b"
API_SECRET = "d75386e8e783823200ef0ae5ed0e2c94"

url = "https://api.mailjet.com/v3.1/send"

data = {
    "Messages": [
        {
            "From": {
                "Email": "haidaralifawwaz@gmail.com",
                "Name": "Rohis Reminder"
            },
            "To": [
                {
                    "Email": "haidar.nasirodin@gdajogja.sch.id",
                    "Name": "Test User"
                }
            ],
            "Subject": "Test Email",
            "TextPart": "This is a test email from your Rohis reminder system.",
        }
    ]
}

response = requests.post(
    url,
    auth=HTTPBasicAuth(API_KEY, API_SECRET),
    json=data
)

print(response.status_code)
print(response.text)
