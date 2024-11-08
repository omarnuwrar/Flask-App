from flask import Flask, render_template

app = Flask(__name__)

# Define the URL and headers for the initial request
url = "https://huggingface.co/chat/conversation"
headers = {
    "Content-Type": "application/json",
    "Cookie": "token=LdeOqPFByfVHXYRcTqdmowtNLCxediADEHZFBibXkaZcHYHtMrYKFEPndUUEyPFTajezjuHTHeStDeabkwbMUoLKzpCFmhmZSIFKvvwWiWHSFdNfoRVKbWuIVTLikIdR; __stripe_mid=06f6506e-e1bc-41c6-88f9-a8b3802c925085fa8e; hf-chat=8881bae7-9647-4cf3-8f8a-59de9f530c82; aws-waf-token=c27f90fe-f8c3-4742-90c7-68e483c93599:DgoAdG6NUVMZAAAA:r3I9urfTNs3M0F/LjKVi3zAL+W3UZ75yLE9SiEnPGsQYZP0qzmo+WNCDXxIacFoPHw5nNHpjZ4dQST/YIFy7vKeVv/fYbrruLJXXYULp2eIxZjmMqmQWZBBqEulrGWvuKpBWymHxyVlJxw6lysVg5ef1amEXPJzaVwdaRiYsNipGTPdiokAbL9k1wunKnirpX3cg3QN9LFeejYP/ZYbiaIciKlxtmnZ+Dlqd5/lh7Uw4jobTLNBRMRN67qZZyooQhmQbW4E="  # Replace with your actual cookie
}
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/chat', methods=['POST'])
def chat():
    print("Received request:", request.json)  # Add this line
    user_message = request.json.get('message')
    
    # Step 2: Define the payload for the POST request
    payload = {
        "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "preprompt": ""
    }

    # Step 3: Make the POST request to get the conversation ID
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    # Step 4: Check if the request was successful and extract conversation ID
    if response.status_code == 200:
        conversation_data = response.json()
        conversation_id = conversation_data['conversationId']
        
        # Step 5: Use the conversation ID to fetch additional data
        url_data = f"https://huggingface.co/chat/conversation/{conversation_id}/__data.json?x-sveltekit-invalidated=01"
        response_data = requests.get(url_data, headers=headers)

        # Step 6: Check if the request was successful and extract the ID
        if response_data.status_code == 200:
            data = response_data.json()
            try:
                extracted_id = data['nodes'][1]['data'][3]
            except (KeyError, IndexError) as e:
                return jsonify({"error": f"Error extracting ID: {e}"}), 500
            
            # Step 7: Use the extracted ID for another request
            url_final = f"https://huggingface.co/chat/conversation/{conversation_id}"
            headers_final = {
                "Accept": "/",
                "Cookie": headers["Cookie"],
                "Origin": "https://huggingface.co",
                "Referer": f"https://huggingface.co/chat/conversation/{conversation_id}",
            }

            data_final = {
                "data": json.dumps({
                    "inputs": user_message,
                    "id": extracted_id,
                    "is_retry": False,
                    "is_continue": False,
                    "web_search": False,
                    "tools": []
                })
            }

            # Step 8: Sending the final POST request
            response_final = requests.post(url_final, headers=headers_final, data=data_final)

            # Step 9: Print the response text
            if response_final.status_code == 200:
                response_lines = response_final.text.strip().splitlines()
                final_answer = None
                
                for line in response_lines:
                    try:
                        json_line = json.loads(line)
                        if json_line.get("type") == "finalAnswer":
                            final_answer = json_line.get("text")
                            break
                    except json.JSONDecodeError:
                        continue
                
                if final_answer:
                    return jsonify({"final_answer": final_answer}), 200
                else:
                    return jsonify({"error": "Final answer not found in the response."}), 500
            else:
                return jsonify({"error": f"Final request failed with status code: {response_final.status_code}"}), 500
        else:
            return jsonify({"error": f"Failed to retrieve data: {response_data.status_code}"}), 500
    else:
        return jsonify({"error": f"Request failed with status code: {response.status_code}"}), 500


if __name__ == '__main__':
    app.run(debug=True)
