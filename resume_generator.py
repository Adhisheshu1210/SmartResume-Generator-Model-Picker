def list_models_via_rest(client):
    try:
        # Make a request to the correct API endpoint
        response = client.models().list().execute()  # Change to v1 if needed 

        # Check if the response is successful
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"HTTP error {response.status_code}: {response.text}")
    except Exception as e:
        # Handle exceptions gracefully
        print(f'An error occurred: {str(e)}')
        return None
