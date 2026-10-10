import requests
from django.conf import settings


def send_sms(phone_number, message):
    """
    Sends an SMS message using Infobip's API.

    Parameters:
      phone_number (str): The recipient's phone number.
      message (str): The text message to send.

    Returns:
      dict: The JSON response from the Infobip API.
    """
    # Build the API endpoint URL. Adjust if your Infobip account uses a different endpoint.
    url = f"{settings.INFOBIP_BASE_URL}/sms/2/text/advanced"

    # Prepare the headers with your API key.
    headers = {
        "Authorization": f"App {settings.INFOBIP_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Construct the payload with sender, destination, and text message.
    payload = {
        "messages": [
            {
                "from": settings.INFOBIP_SENDER,
                "destinations": [{"to": phone_number}],
                "text": message,
            }
        ]
    }

    # Make the POST request to Infobip.
    response = requests.post(url, json=payload, headers=headers)

    # Optionally, you can add error handling here:
    if response.status_code != 200:
        # Log error or raise an exception if needed.
        response.raise_for_status()

    return response.json()
