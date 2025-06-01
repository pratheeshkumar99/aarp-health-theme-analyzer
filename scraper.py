import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import pandas as pd 
from tqdm import tqdm
import os

def extract_article_Links(base_url , output_file = "links.txt" , max_depth = 3):
    """
    Crawl the website starting from base_url to find health article links.
    
    Args:
        base_url (str): The starting URL for crawling
        output_file (str): File to save the extracted links
        max_depth (int): Maximum crawling depth
        
    Returns:
        set: Set of extracted article links
    """
    visited = set()
    links = set()
    
    def visit(url , depth):
      if depth > max_depth or url in visited:
        return

      visited.add(url)

      try:
        response = requests.get(url)
        response.raise_for_status()

      except requests.RequestException as e:
        raise Exception(f"Error visiting {url} : {e}")
        # print(f"Error visiting {url} : {e}")
        # return

      soup = BeautifulSoup(response.content , "html.parser")

      for a in soup.find_all("a" , href=True):
        href = a["href"]

        if re.match(r"^/health/.*", href):
          link = urljoin(base_url , href)

          if link not in links:
            links.add(link)
            visit(link , depth + 1)

    try:

      visit(base_url , 0)

      # Ensure directory exists for output file
      os.makedirs(os.path.dirname(output_file) or '.', exist_ok=True)
      
      with open(output_file , "w") as f:
        for link in links:
          f.write(link + "\n")
      print(f"{len(links)} Links saved to {output_file}")
      return links
    
    except Exception as e:
        print(f"Error in extract_article_Links:")
        return set()

def get_content_from_link(link , df):
    """
    Extract content from a single article link.
    
    Args:
        link (str): The article URL to scrape
        df (DataFrame): DataFrame to store the results
    """
    try:
        response = requests.get(link)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error visiting {link} : {e}")
        return

    soup = BeautifulSoup(response.content, "html.parser")
    contents = soup.find_all('div', class_="articlecontentfragment")

    content = ""
    for c in contents:
        content += c.get_text()

    cleaned_content = re.sub(r'\s+', ' ', content).strip()
    df.loc[len(df)] = [link, cleaned_content]


def extract_article_content(link="https://www.aarp.org/health"):
    """
    Main function to extract and process article content from links.
    
    Args:
        link (str): Base URL to scrape health articles from
        
    Returns:
        DataFrame: DataFrame containing article links and content
    """
    try:

      # First extract the links
      links_set = extract_article_Links(link)

      # If links.txt exists, read from it; otherwise, use the set
      if os.path.exists("links.txt"):
            with open("links.txt", "r") as file:
                links = [line.strip() for line in file]
      else:
            links = list(links_set)

      if not links:
            print("No links found. Check the base URL and network connection.")
            return pd.DataFrame(columns=["Link", "Content"])

      print(f"Found {len(links)} links")

      # Create DataFrame to store results
      df = pd.DataFrame(columns=["Link" , "Content"])
      for link in tqdm(links, desc="Processing articles"):
          get_content_from_link(link, df)

      # Ensure results directory exists
      os.makedirs("results", exist_ok=True)

      # Save results to CSV
      df.to_csv("results/health_articles_depth_3.csv" , index=False)
      print(f"Saved {len(df)} articles to results/health_articles_depth_3.csv")


      return df
    
    except Exception as e:
      print(f"Error in extract_article_content:")
      # Return empty DataFrame to avoid breaking the pipeline
      raise Exception(f"Error in extract_article_content:")






