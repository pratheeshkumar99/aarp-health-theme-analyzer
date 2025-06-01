from scraper import extract_article_content
from cleaner import clean_articles
from summarizer import summarize_article
from cluster import cluster_articles
from utils import create_document_to_theme_count_mapping_json, dump_json, load_env_variables
from tagger import article_tagger
import os
import sys



def main(link):
    """
    Main pipeline function that orchestrates the entire workflow:
    1. Scrape articles from the provided link
    2. Clean and preprocess the articles
    3. Tag articles with keywords
    4. Summarize articles
    5. Cluster articles into themes
    6. Generate output files
    
    Args:
        link (str): Base URL to scrape health articles from
    """
    try:
        # Load environment variables - will raise exception if keys missing
        env_vars = load_env_variables()
        
        # Create results directory
        os.makedirs("results", exist_ok=True)

        # Scraping - raises exception if fails
        print("Scraping articles...")
        df = extract_article_content(link)
        if df.empty:
            print("Error: No articles found. Check the URL and network connection.")
            raise Exception("No articles found")
        
 
        # Cleaning - raises exception if fails
        print("Cleaning articles...")
        cleaned_df = clean_articles(df)
        if cleaned_df.empty:
            print("Error: No valid articles after cleaning. Check content quality.")
            raise Exception("No valid articles after cleaning")
        
        cleaned_df = cleaned_df[:20] # Limit to 20 articles for testing/development

        # Save intermediate result
        try:
            cleaned_df.to_csv("results/cleaned_articles.csv", index=False)
            print(f"Saved {len(cleaned_df)} cleaned articles to results/cleaned_articles.csv")
        except Exception as e:
            print(f"Warning: Could not save intermediate CSV: {e}")
            # Continue pipeline despite CSV save error

        # Tagging - only step that continues on failure
        print("Tagging articles...")
        try:
            document_keywords = article_tagger(cleaned_df)
            try:
                dump_json(document_keywords, 'results/document_keywords.json')
            except Exception as json_e:
                print(f"Warning: Could not save tagging results: {json_e}")
        except Exception as e:
            print(f"Error during article tagging: {e}")
            print("Continuing with next steps...")

        # Summarizing - raises exception if fails
        print("Summarizing articles...")
        summarized_df = summarize_article(cleaned_df)
        
        # Save intermediate summarized results
        try:
            summarized_df.to_csv("results/summarized_articles.csv", index=False)
        except Exception as e:
            print(f"Warning: Could not save summarized CSV: {e}")
            # Continue pipeline despite CSV save error

        # Clustering - raises exception if fails
        print("Clustering articles...")
        article_to_theme = cluster_articles(summarized_df)
        
        # Save final results
        try:
            dump_json(article_to_theme, 'results/article_to_theme.json')
            create_document_to_theme_count_mapping_json(summarized_df, 'results/article_to_theme.json')
            print("Pipeline completed successfully!")
        except Exception as e:
            print(f"Error saving final results: {e}")
            raise Exception("Failed to save clustering results")

    except Exception as e:
        print(f"Critical error in main pipeline: {e}")
        print("Pipeline terminated due to an error.")


if __name__ == "__main__":
    # Allow command-line argument for URL or use default
    link = sys.argv[1] if len(sys.argv) > 1 else "https://www.aarp.org/health"
    main(link)
