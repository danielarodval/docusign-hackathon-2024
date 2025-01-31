def response_generator(prompt, state):
    
    try:
        # Check if selected_agreement exists and is a dictionary
        if hasattr(state, 'selected_agreement') and isinstance(state.selected_agreement, dict):
            url_ext = "/api/chat"
            # Convert agreement to JSON string for context
            agreement_context = json.dumps(state.selected_agreement, separators=(',', ':'))
            # Force-escape all existing double quotes
            #escaped_agreement_context = agreement_context.replace('"', r'\"')
            full_context = [
                {
                    'role': 'system',
                    'content': f"Agreement Context: {agreement_context}"
                },
                *state.messages,
                {
                    'role': 'user',
                    'content': prompt
                }
            ]

            DATA = {
                "model": "mistral",
                "messages": full_context
            }

            #print(json.dumps(DATA, indent=2))
            response = requests.post(URL+url_ext, json=DATA, headers={"Content-Type": "application/json"})

            # split the response by newlines and filter our empty lines
            response_lines = [line for line in response.text.strip().split("\n") if line]
            # parse each line as json
            response_dicts = [json.loads(line) for line in response_lines]
            # format as string
            response_text = ''.join(
                d['message']['content']
                for d in response_dicts
                if 'message' in d and 'content' in d['message']
            )

        else:
            url_ext = "/api/generate"
            DATA = {
                "model": "mistral",
                "prompt": prompt
            }
            response = requests.post(URL+url_ext, json=DATA)

            # split the response by newlines and filter our empty lines
            response_lines = [line for line in response.text.strip().split("\n") if line]
            # parse each line as json
            response_dicts = [json.loads(line) for line in response_lines]
            # format as string
            response_text = ''.join(
                response_dict.get('response', '') 
                for response_dict in response_dicts
            )
        
        #print(response.text)
   
        
        #print(response_text)
        return response_text
    except Exception as e:
        logging.error(f"Error during response generation: {str(e)}")
        return f"An error occurred: {str(e)}"

def display_response(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)