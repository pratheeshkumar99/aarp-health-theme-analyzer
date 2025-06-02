from groq import Groq
import time
from tqdm import tqdm
from utils import load_env_variables

def tag(content):
    """
    Extract 5 important keywords from health article content using the Groq API.
    
    Args:
        content (str): The article content to analyze
        
    Returns:
        list: List of 5 keywords representing the main topics of the article
    """
    try:
        env_vars = load_env_variables()
        # Check if API key is available
        if not env_vars["groq_api_key"]:
            print("Error: Groq API key not found. Check your environment variables.")
            return ["API key missing"]
        
        client = Groq(api_key=env_vars["groq_api_key"])
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert medical content analyst. "
                        "Identify the 5 most important keywords that represent "
                        "the main topics of a health article. "
                        "Provide ONLY the 5 keywords separated by commas, no additional text."
                    )
                },
                {
                    "role": "user", 
                    "content": f"Extract exactly 5 keywords from this health article:\n\n{content}"
                }
            ],
            temperature=0.1
        )
        
        keywords_text = completion.choices[0].message.content.strip()
        keywords = [k.strip() for k in keywords_text.split(',')]
        # Ensure exactly 5 keywords are returned
        keywords = keywords[:5]
        
        return keywords
    
    except Exception as e:
        print(f"Error in tag function: {e}")
        return ["Error extracting keywords"]
    
        

def article_tagger(df):
    """
    Process all articles in the DataFrame to extract keywords.
    
    Args:
        df (DataFrame): DataFrame containing article content
        
    Returns:
        dict: Mapping of article links to their extracted keywords
    """

    document_to_tags = {}
    
    for index, row in tqdm(df.iterrows(), total=len(df)):
        try:
             # Skip articles with missing content
            if not isinstance(row.get('Content'), str) or row.get('Content', '').strip() == '':
                print(f"Skipping article {index}: Missing or empty content")
                document_to_tags[row.get('Link', f"unknown_{index}")] = []
                continue

            # Extract content and link
            content = row['Content']
            keywords = tag(content)
            document_to_tags[row['Link']] = keywords

            # Rate limiting
            if (index + 1) % 25 == 0:
                print(f"Processed {index + 1} articles. Taking a 60-second break to respect rate limits...")
                time.sleep(60)
            else:
                time.sleep(2)
                
        except Exception as e:
            print(f"Error processing article {index}: {e}")
            raise Exception(f"Error processing article {index}: {e}")
    
    return document_to_tags

