import requests

# Define the API endpoint
url = "http://localhost:8000/chat"

# Define the headers
headers = {
    "Content-Type": "application/json"
}

# Define the request payload
data = {
    "messages": [
        {
            "role": "user",
            "content": "Hello, can you introduce yourself?"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 50
}

# Send the POST request to the /chat endpoint
response = requests.post(url, headers=headers, json=data)

# Print the response JSON
print(response.status_code)  
print(response.json())    
