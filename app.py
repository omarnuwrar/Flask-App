from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    # Define the URL and headers
    url = "https://huggingface.co/chat/conversation"
    headers = {
        "Content-Type": "application/json",
        "Cookie": "token=LdeOqPFByfVHXYRcTqdmowtNLCxediADEHZFBibXkaZcHYHtMrYKFEPndUUEyPFTajezjuHTHeStDeabkwbMUoLKzpCFmhmZSIFKvvwWiWHSFdNfoRVKbWuIVTLikIdR; __stripe_mid=06f6506e-e1bc-41c6-88f9-a8b3802c925085fa8e; hf-chat=8881bae7-9647-4cf3-8f8a-59de9f530c82; aws-waf-token=c27f90fe-f8c3-4742-90c7-68e483c93599:DgoAdG6NUVMZAAAA:r3I9urfTNs3M0F/LjKVi3zAL+W3UZ75yLE9SiEnPGsQYZP0qzmo+WNCDXxIacFoPHw5nNHpjZ4dQST/YIFy7vKeVv/fYbrruLJXXYULp2eIxZjmMqmQWZBBqEulrGWvuKpBWymHxyVlJxw6lysVg5ef1amEXPJzaVwdaRiYsNipGTPdiokAbL9k1wunKnirpX3cg3QN9LFeejYP/ZYbiaIciKlxtmnZ+Dlqd5/lh7Uw4jobTLNBRMRN67qZZyooQhmQbW4E="  # Replace with your actual cookie
    }

    # Define the payload
    payload = {
        "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "preprompt": ""
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Initialize ID variable
    id_result = None

    # Check if the request was successful
    if response.status_code == 200:
        json_response = response.json()
        id_result = json_response.get('id', 'No ID found')  # Adjust according to your response structure
    else:
        id_result = f"Request failed with status code: {response.status_code}"

    return render_template('index.html', id_result=id_result)

if __name__ == '__main__':
    app.run(debug=True)
