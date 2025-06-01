import json
import os
from dotenv import load_dotenv
from groq import Groq
from langchain_community.chat_models import ChatOpenAI




def validate_api_keys(groq_api_key, openai_api_key):
    """
    Validate API keys by making test calls to both APIs.
    
    Args:
        groq_api_key (str): Groq API key to validate
        openai_api_key (str): OpenAI API key to validate
        
    Raises:
        Exception: If either API key is invalid
    """
    # Validate the Groq API key with a simple test call
    try:
        groq_client = Groq(api_key=groq_api_key)
        # Make a minimal API call to check if the key is valid
        groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{"role": "user", "content": "test"}],
            max_tokens=1  # Minimal tokens to save quota
        )
    except Exception as e:
        raise Exception(f"Invalid Groq API key: {str(e)}")
        
    # Validate the OpenAI API key with a simple test call
    try:
        # Use the same ChatOpenAI class that will be used later
        chat = ChatOpenAI(
            api_key=openai_api_key,
            model_name="gpt-4o",  # Use a model that's likely available
            max_tokens=1  # Minimal tokens to save quota
        )
        # Make a minimal test call
        chat.invoke("test")
    except Exception as e:
        raise Exception(f"Invalid OpenAI API key: {str(e)}")
    



def load_env_variables():
    """
    Load environment variables from a specific .env file located in the same
    directory as the script, and validate the API keys with a test call.
    
    Returns:
        dict: Dictionary containing API keys and other environment variables
    """
    try:
        # Get the directory where the script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the .env file (in the same directory as the script)
        env_path = os.path.join(script_dir, '.env')
        
        # Check if the .env file exists
        if not os.path.exists(env_path):
            raise Exception(f".env file not found at {env_path}")
        
        # Load only from this specific .env file, ignoring system environment
        # Override=True ensures it overwrites any existing environment variables
        load_dotenv(dotenv_path=env_path, override=True)
        
        # Get API keys from the loaded environment
        groq_api_key = os.getenv("GROQ_API_KEY")
        openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Check if keys exist
        if not groq_api_key:
            raise Exception(f"GROQ_API_KEY not found in .env file at {env_path}")
        
        if not openai_api_key:
            raise Exception(f"OPENAI_API_KEY not found in .env file at {env_path}")
            
        # Validate both API keys using the separate validation function
        validate_api_keys(groq_api_key, openai_api_key)
        
        return {
            "groq_api_key": groq_api_key,
            "openai_api_key": openai_api_key
        }
    except Exception as e:
        print(f"Error loading or validating environment variables: {e}")
        raise Exception(f"Error loading or validating environment variables: {e}")


        


def create_document_to_theme_count_mapping_json(df,themes_json_path):
    """
    Create a mapping of themes to document links and counts.
    
    Args:
        df (DataFrame): DataFrame containing article data
        themes_json_path (str): Path to the JSON file with theme data
    """
    try:
        with open(themes_json_path, 'r') as file:
            themes = json.load(file)

        # Convert string IDs to integers
        themes = {theme: [int(i) for i in ids] for theme, ids in themes.items()}

        # Initialize empty mapping
        theme_mapping = {}

        # Create mapping of themes to document links and counts
        for theme, ids in themes.items():
            links = df[df['Id'].isin(ids)]['Link'].tolist()
            theme_mapping[theme] = {
                'links': links,
                'count': len(links)
            }

        output_file = 'results/cluster_results.json'
        with open(output_file, 'w') as file:
            json.dump(theme_mapping, file, indent=2)

        print(f"Mapping saved to {output_file}")

    except Exception as e:
        print(f"Error creating theme mapping: {e}")
        # Create a minimal output file to prevent downstream errors
        try:
            with open('results/cluster_results.json', 'w') as file:
                json.dump({}, file)
            print("Created empty mapping file due to error")
        except:
            print("Failed to create even an empty mapping file")




def dump_json(data, file_path):
    """
    Save data as JSON to the specified file path.
    
    Args:
        data: Data to be serialized to JSON
        file_path (str): Output file path
    """

    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w') as f:
            json.dump(data, f)
        print(f"Successfully saved data to {file_path}")
        
    except Exception as e:
        print(f"Error saving JSON to {file_path}: {e}")

\

