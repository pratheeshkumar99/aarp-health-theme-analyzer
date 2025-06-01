from groq import Groq
from tqdm import tqdm
import time
from utils import load_env_variables

def summarize(content):
    """
    Generate a concise summary of health article content using the Groq API.
    
    Args:
        content (str): The article content to summarize
        
    Returns:
        str: A 3-4 sentence summary of the article
    """
    try:
        env_vars = load_env_variables()

        # Check if API key is available
        if not env_vars.get("groq_api_key"):
            print("Error: Groq API key not found. Check your environment variables.")
            return "Error: API key missing"

        client = Groq(api_key=env_vars["groq_api_key"])
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",  
            messages=[
                {
                    "role": "system",
                    "content": (
                        # "You are an expert medical journalist. "
                        # "Your job is to capture the essence of a health article by naming its main topic, "
                        # "summarizing the most important facts or insights, and noting any unique perspective. "
                        # "Write in 3–4 clear sentences."
                        "You are an expert medical journalist. "
                        "Your job is to capture the essence of a health article by naming its main topic, "
                        "summarizing the most important facts or insights, and noting any unique perspective. "
                        "Write in 3–4 clear sentences. "
                        "IMPORTANT: Start directly with the content. Do NOT begin with phrases like "
                        "'Here is a summary', 'The article discusses', or 'This article explores'. "
                        "Jump straight into the medical content."
                    )
                },
                {
                    "role": "user", 
                    "content": (
                        # "Summarize the following article content, focusing on:\n"
                        # "1) The central theme or question it addresses.\n"
                        # "2) The key findings or recommendations.\n"
                        # "3) Any novel or surprising insight.\n\n"
                        # f"{content}"
                        "Summarize the following article content, focusing on:\n"
                        "1) The central theme or question it addresses.\n"
                        "2) The key findings or recommendations.\n"
                        "3) Any novel or surprising insight.\n\n"
                        "Remember: Start directly with the medical content, no introductory phrases.\n\n"
                        f"{content}"
                    )
                }
            ],
            temperature=0.2
        )
        
        return completion.choices[0].message.content.strip()
    
    except Exception as e:

        print(f"Error in summarize function: {e}")
        return f"Error summarizing content: {str(e)[:100]}"


def summarize_article_with_rate_limits(dataframe):
    """
    Summarize articles with Groq rate limit handling
    
    Args:
        dataframe (DataFrame): DataFrame containing articles to summarize
        
    Returns:
        DataFrame: DataFrame with added 'Summary' column
    """
    processed_count = 0
    for index, row in tqdm(dataframe.iterrows(), total=len(dataframe), desc="Processing articles"):
        try:

            content = row['Content']
            summary = summarize(content)
            dataframe.at[index, 'Summary'] = summary
            
            processed_count += 1
         
            # Rate limit handling
            if processed_count % 25 == 0:
                print(f"\nProcessed {processed_count}/{len(dataframe)} articles")
                print("Taking 60-second break to respect rate limits...")
                time.sleep(60)  
            else:
                time.sleep(2) 
                
        except Exception as e:
            raise Exception(f"Error processing article {index}: {e}")

    
    print(f"\nCompleted! Processed {processed_count} articles")
    return dataframe

def summarize_article(dataframe):
    """
    Main function - wrapper for backwards compatibility
    
    Args:
        dataframe (DataFrame): DataFrame containing articles to summarize
        
    Returns:
        DataFrame: DataFrame with added 'Summary' column
    """
    try:
        return summarize_article_with_rate_limits(dataframe)
    except Exception as e:
        raise Exception(f"Error in summarize_article: {e}")

