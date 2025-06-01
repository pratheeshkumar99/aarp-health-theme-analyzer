import pandas as pd

def add_id(df):
    """
    Add sequential ID column to the DataFrame.
    
    Args:
        df (DataFrame): Input DataFrame
        
    Returns:
        DataFrame: DataFrame with added 'Id' column
    """
    df["Id"] = range(len(df))
    return df

def clean_articles(df):
    """
    Remove rows with empty content and add ID column.
    
    Args:
        df (DataFrame): Input DataFrame with article data
        
    Returns:
        DataFrame: Cleaned DataFrame with non-empty content
    """
    try:
        # Make a copy to avoid modifying the original
        df_copy = df.copy()
        
        # Handle empty DataFrame
        if df_copy.empty:
            print("Warning: Empty DataFrame provided to clean_articles")
            return df_copy
            
        # Handle missing 'Content' column
        if 'Content' not in df_copy.columns:
            print("Warning: 'Content' column not found in DataFrame")
            df_copy['Content'] = ''

        # Remove rows with empty content
        df_clean = df_copy[df_copy['Content'].notna() & (df_copy['Content'].str.strip() != '')].copy()
        print(f"Removed {len(df_copy) - len(df_clean)} rows with empty content")
        
        # Add ID column
        df_clean = add_id(df_clean)
        
        return df_clean
    
    except Exception as e:
        print(f"Error in clean_articles: {e}")
        # Return original DataFrame to avoid breaking the pipeline
        raise Exception(f"Error in clean_articles: {e}")
