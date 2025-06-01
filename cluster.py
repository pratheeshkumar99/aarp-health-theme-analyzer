import os
import json
import pandas as pd
from typing import List, Dict, Optional, Set, Tuple
from pydantic import BaseModel, Field
from langchain.schema import HumanMessage
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain_community.chat_models import ChatOpenAI
from collections import defaultdict
from utils import load_env_variables


class ThemeMap(BaseModel):
    """Model for theme mapping output."""
    doc_to_theme: Dict[str, str] = Field(..., description="id→theme")
    new_theme_names: List[str]


class Article(BaseModel):
    """Model for article data."""
    article_id: str
    summary: str
    url: Optional[str] = None


def set_api_key(api_key: str) -> None:
    """
    Set the OpenAI API key.
    
    Args:
        api_key (str): OpenAI API key to set in environment variables
    """
     
    os.environ["OPENAI_API_KEY"] = api_key


def batch_articles(articles: List[Article], batch_size: int = 5) -> List[List[Article]]:
    """
    Split articles into batches for processing.
    
    Args:
        articles (List[Article]): List of Article objects to batch
        batch_size (int): Number of articles per batch
        
    Returns:
        List[List[Article]]: List of article batches
    """
    return [articles[i : i + batch_size] for i in range(0, len(articles), batch_size)]


def process_batches(
    batches: List[List[Article]], 
    theme_names_set: Set[str],
    article_to_theme: Dict[str, str],
    llm,
    base_parser,
    fixing_parser,
    prompt_template: str
) -> Tuple[Set[str], Dict[str, str]]:
    

    """
    Process batches of articles to map them to themes.
    
    Args:
        batches: List of article batches
        theme_names_set: Set of existing theme names
        article_to_theme: Dictionary mapping article IDs to themes
        llm: Language model instance
        base_parser: Pydantic output parser
        fixing_parser: Output fixing parser for error correction
        prompt_template: Template string for the prompt
        
    Returns:
        Tuple containing updated theme names set and article-to-theme mapping
    """


    print("Processing batches...")
    for batch_idx, batch in enumerate(batches):
        try:
                # Create JSON strings for existing themes and new articles
            existing_json = json.dumps(sorted(theme_names_set), indent=2)
            new_json = json.dumps([a.dict(exclude_none=True) for a in batch],
                                indent=2, ensure_ascii=False)
            
            # Format the prompt with the existing themes and new articles
            prompt = prompt_template.format(
                existing_themes_json=existing_json,
                new_articles_json=new_json
            )

            
            response = llm.invoke([HumanMessage(content=prompt)])
            raw_output = response.content

            # Parse the output using the base parser
            try:
                parsed = base_parser.parse(raw_output)
            except:
                parsed = fixing_parser.parse(raw_output)

            # Update the theme names set and article-to-theme mapping
            theme_names_set.update(parsed.new_theme_names)
            article_to_theme.update(parsed.doc_to_theme)

            # Add a progress indicator
            # Add progress indicator
            print(f"Processed batch {batch_idx + 1}/{len(batches)}, " 
                    f"themes so far: {len(theme_names_set)}")
                

        except Exception as e:
            raise Exception(f"Error processing batch {batch_idx + 1}: {e}")


    return theme_names_set, article_to_theme


def prepare_articles_from_df(df: pd.DataFrame) -> Tuple[List[Article], Dict[str, Dict]]:
    """
    Convert dataframe to list of Article objects and create article lookup dict.
    
    Args:
        df (DataFrame): DataFrame containing article data
        
    Returns:
        Tuple containing list of Article objects and article lookup dictionary
    """
    try:
            
        # Create list of dictionaries for each article
        data = []
        for index, row in df.iterrows():
            curr = {
                "Article_id": str(row["Id"]),
                "Link": row.get("Link", None),
                "Summary": row["Summary"]
            }
            data.append(curr)

        # Create article lookup dictionary
        article_by_id = {article["Article_id"]: article for article in data}


        # Create Article objects
        articles = [
            Article(
                article_id=article["Article_id"], 
                summary=article["Summary"], 
                url=article.get("Link")
            ) 
            for article in data
        ]
        return articles, article_by_id
    
    except Exception as e:
        print(f"Error preparing articles from DataFrame:")

        raise Exception(f"Error preparing articles from DataFrame: {e}")




def get_theme_mapping_prompt() -> str:

    """
    Return the prompt template for theme mapping.
    
    Returns:
        str: The prompt template string
    """


    return """
    You are a **Theme Mapper**.

    TASK
    ----
    **PRIORITY ORDER:**
    1. **FIRST**: Try to map articles to existing themes if they fit
    2. **SECOND**: Look for 2+ articles that share similar topics and create ONE shared theme name for them
    3. **LAST RESORT ONLY**: Give an article its own theme if it absolutely cannot be grouped with anything else

    **Focus on GROUPING articles together rather than creating individual themes.**

    Return **only** JSON:

    {{
    "doc_to_theme": {{"<article_id>":"<theme_name>" }},
    "new_theme_names": ["string", …]
    }}

    EXAMPLES:

    **EXAMPLE A - Empty existing themes (first batch):**
    existing_themes: []
    new_articles: [
    {{"article_id": "0", "summary": "Eye exams can detect early Alzheimer's signs..."}},
    {{"article_id": "1", "summary": "Fiber intake important for digestive health..."}},
    {{"article_id": "2", "summary": "Common eye conditions in older adults like cataracts..."}},
    {{"article_id": "3", "summary": "Sunglasses protect against UV damage to eyes..."}},
    {{"article_id": "4", "summary": "Vitamin deficiencies cause fatigue and weakness..."}}
    ]

    Expected output:
    {{
    "doc_to_theme": {{
        "0": "Eye Health",
        "2": "Eye Health",
        "3": "Eye Health",
        "1": "Nutrition",
        "4": "Nutrition"
    }},
    "new_theme_names": ["Eye Health", "Nutrition"]
    }}

    **EXAMPLE B - Mix of existing themes + new grouping:**
    existing_themes: ["Eye Health", "Nutrition"]
    new_articles: [
    {{"article_id": "5", "summary": "New contact lens technology improves vision..."}},
    {{"article_id": "6", "summary": "Heart disease prevention through exercise..."}},
    {{"article_id": "7", "summary": "Different types of cardio workouts for seniors..."}},
    {{"article_id": "8", "summary": "Protein supplements for muscle building..."}}
    ]

    Expected output:
    {{
    "doc_to_theme": {{
        "5": "Eye Health",
        "6": "Heart Health",
        "7": "Heart Health",
        "8": "Nutrition"
    }},
    "new_theme_names": ["Heart Health"]
    }}

    **EXAMPLE C - Mostly existing themes + one unique:**
    existing_themes: ["Eye Health", "Nutrition", "Heart Health"]
    new_articles: [
    {{"article_id": "9", "summary": "Glaucoma screening recommendations..."}},
    {{"article_id": "10", "summary": "Omega-3 fatty acids in fish..."}},
    {{"article_id": "11", "summary": "Rare genetic disorder affects 1 in million people..."}}
    ]

    Expected output:
    {{
    "doc_to_theme": {{
        "9": "Eye Health",
        "10": "Nutrition",
        "11": "Rare Genetic Disorders"
    }},
    "new_theme_names": ["Rare Genetic Disorders"]
    }}


    **REMEMBER**: Multiple articles about similar topics should share the same theme name. Look for patterns like:
    - Eye/vision topics → same theme
    - Nutrition/diet/vitamins → same theme
    - Brain/cognitive/mental health → same theme
    - Disease prevention/vaccination/hygiene → same theme

    ────────────────────────
    NOW PROCESS THE REAL INPUT
    ────────────────────────
    existing_themes:
    {existing_themes_json}

    new_articles:
    {new_articles_json}
    """


def cluster(df: pd.DataFrame, api_key: str = None, batch_size: int = 5, model_name: str = "gpt-4") -> Tuple[Set[str], Dict[str, str]]:
    """
    Main function to cluster articles based on their summaries.
    
    Args:
        df: DataFrame containing at least a 'Summary' column and optionally 'Link' column
        api_key: OpenAI API key (optional if already set in environment)
        batch_size: Number of articles to process in each batch
        model_name: The OpenAI model to use for clustering
        
    Returns:
        Tuple containing:
        - Set of theme names
        - Dictionary mapping article IDs to themes
    """

    try :

        #Set the API key if provided
        if api_key:
            set_api_key(api_key)

        # Check if API key is available in environment
        if not os.environ.get("OPENAI_API_KEY"):
            raise Exception("Warning: OpenAI API key not found. Check your environment variables.")
        
        # Prepare articles from DataFrame
        articles, article_by_id = prepare_articles_from_df(df)

 
        # Split articles into batches
        batches = batch_articles(articles, batch_size=batch_size)

        # Initialize parsers
        base_parser = PydanticOutputParser(pydantic_object=ThemeMap)

        
        fixing_parser = OutputFixingParser.from_llm(
            parser=base_parser,
            llm=ChatOpenAI(model_name="gpt-4o", temperature=0),
        )
        
        
        #Set up the language model
        # Setup LLM
        try:
            llm = ChatOpenAI(model_name=model_name, temperature=0.1)
        except Exception as e:
            print(f"Error initializing ChatOpenAI with model {model_name}: {e}")
            print("Trying with gpt-4o as fallback")
            try:
                llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)
            except Exception as e2:
                print(f"Error initializing fallback model: {e2}")
                raise Exception(f"Error initializing the language model for clustering")
        
        # Set up the prompt template
        prompt_template = get_theme_mapping_prompt()

        # Initialize theme names set and article-to-theme mapping
        theme_names_set: Set[str] = set()
        article_to_theme: Dict[str, str] = {}

        # Process batches
        theme_names_set, article_to_theme = process_batches(
            batches,
            theme_names_set,
            article_to_theme,
            llm,
            base_parser,
            fixing_parser,
            prompt_template
        )

            
        return theme_names_set, article_to_theme
    
    except Exception as e:
        raise Exception(f"Error in clustering: {e}")


def reformat_results(article_to_theme):
    """
    Reorganize article-to-theme mapping to theme-to-articles mapping.
    
    Args:
        article_to_theme (dict): Dictionary mapping article IDs to themes
        
    Returns:
        dict: Dictionary mapping themes to lists of article IDs
    """
    try:
        theme_groups = defaultdict(list)
        for article_id, theme in article_to_theme.items():
            theme_groups[theme].append(article_id)
        return dict(theme_groups)
    except Exception as e:
        raise Exception(f"Error reformatting results: {e}")




def cluster_articles(df):
    """
    Main wrapper function for clustering articles.
    
    Args:
        df (DataFrame): DataFrame containing article data
        
    Returns:
        dict: Theme groups mapping themes to lists of article IDs
    """

    try:
        env_vars = load_env_variables()
        api_key = env_vars.get("openai_api_key")
          
      
        # Run clustering
        themes, article_mapping = cluster(df, api_key)
        
        # Reformat results
        theme_groups = reformat_results(article_mapping)
        
        return theme_groups
    
    except Exception as e:
        print(f"Error in cluster_articles: {e}")
        raise Exception("Error")




