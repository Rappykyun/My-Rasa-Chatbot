import json
import yaml
import os

def convert_intents_to_rasa_format(input_file):
    # Read the JSON file
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Initialize data structures
    nlu_data = {"version": "3.1", "nlu": []}
    processed_intents = set()  # Track processed intents
    domain_intents = []
    domain_responses = {}
    stories = []
    rules = []
    
    # Process each intent
    for intent in data['intents']:
        intent_name = intent['tag'].lower().replace(' ', '_')
        
        # Skip if we've already processed this intent
        if intent_name in processed_intents:
            continue
            
        processed_intents.add(intent_name)
        
        # Add to domain intents
        domain_intents.append(intent_name)
        
        # Add to NLU data
        nlu_data["nlu"].append({
            "intent": intent_name,
            "examples": "\n".join([f"- {pattern}" for pattern in intent['patterns']])
        })
        
        # Add to domain responses
        response_key = f"utter_{intent_name}"
        domain_responses[response_key] = [{"text": response} for response in intent['responses']]
        
        # Add to stories
        stories.append({
            "story": f"answer about {intent_name}",
            "steps": [
                {"intent": intent_name},
                {"action": f"utter_{intent_name}"}
            ]
        })
        
        # Add to rules
        rules.append({
            "rule": f"Respond to {intent_name}",
            "steps": [
                {"intent": intent_name},
                {"action": f"utter_{intent_name}"}
            ]
        })
    
    # Create domain content
    domain_content = {
        "version": "3.1",
        "intents": sorted(list(set(domain_intents))),
        "responses": domain_responses,
        "session_config": {
            "session_expiration_time": 60,
            "carry_over_slots_to_new_session": True
        }
    }
    
    # Create content dictionaries
    stories_content = {"version": "3.1", "stories": stories}
    rules_content = {"version": "3.1", "rules": rules}
    
    # Delete existing files
    files_to_delete = ['domain.yml', 'data/nlu.yml', 'data/stories.yml', 'data/rules.yml']
    for file in files_to_delete:
        try:
            os.remove(file)
        except OSError:
            pass
    
    # Create data directory
    os.makedirs('data', exist_ok=True)
    
    # Write all files
    with open('domain.yml', 'w', encoding='utf-8') as f:
        yaml.dump(domain_content, f, allow_unicode=True, default_flow_style=False)
    
    with open('data/nlu.yml', 'w', encoding='utf-8') as f:
        yaml.dump(nlu_data, f, allow_unicode=True, default_flow_style=False)
    
    with open('data/stories.yml', 'w', encoding='utf-8') as f:
        yaml.dump(stories_content, f, allow_unicode=True, default_flow_style=False)
    
    with open('data/rules.yml', 'w', encoding='utf-8') as f:
        yaml.dump(rules_content, f, allow_unicode=True, default_flow_style=False)

if __name__ == "__main__":
    convert_intents_to_rasa_format('intents.json')