import os
import resend

resend.api_key ="re_4gEyKEFT_Fdwkp46rzj1v99TMmPCWJSAR"

params = {
    "from": "Acme <onboarding@resend.dev>",
    "to": ["haidaralifawwaz@gmail.com"],
    "subject": "Hello world",
    "html": "<strong>It works!</strong>"
}

email = resend.Emails.send(params)
print(email)