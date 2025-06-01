# aarp-health-theme-analyzer


<!-- 1. What the repository about? -> Problem statement + aim + how should it be helpful
2. Setup instruction 1. local 2. docker
3. Project Tree
4. Methodology
5. Results - { Keywords & grouping of Articles } #pending
6. Future of scope - optional -->

## Project Overview

### What This Repository Is About

This repository contains the solution to the **AARP Data Science Internship Assignment (May 2025)**. The goal of the assignment is to build an automated system that can collect, analyze, and organize health-related articles from the [AARP Health Channel](https://www.aarp.org/health/) into meaningful themes using **Large Language Models (LLMs)**.


### Problem Statement


The AARP Health Channel publishes hundreds of articles on a wide range of topics—like nutrition, exercise, aging, chronic illnesses, and public health concerns. While this content is informative, it’s unstructured and scattered across many pages. As the number of articles grows, it becomes harder to manually track what’s being published, identify topic trends, or spot content gaps. Doing this by hand takes time, doesn’t scale well, and can lead to inconsistent results.


### Aim

The aim of this project is to create a **fully automated pipeline** that helps AARP make sense of its health articles in a clear, structured way. The system performs the following steps:

- **Scrapes** articles directly from the AARP Health Channel,
- **Cleans and prepares** the content so it's ready for analysis,
- **Generates clear, concise summaries** for each article using large language models (LLMs),
- **Finds recurring patterns and themes** across the articles using semantic analysis,
- And **groups the articles into theme-based clusters** so that AARP can easily see what kinds of health topics are being discussed the most.


### How This Is Helpful

This system transforms unstructured content into strategic business insights with measurable impact:

- **Editorial teams** can identify content gaps and avoid duplication, enabling them to capture more diverse audience segments and improve search rankings by covering under-represented health topics, ultimately driving higher website traffic and membership growth

**Marketing and product teams** can use these theme clusters to guide their outreach and product positioning. Since the articles reflect broader health trends and public concerns, this enables AARP to:

  - Launch targeted campaigns when people need them most (e.g., heat safety education before summer peaks, flu prevention before winter), allowing them to allocate resources strategically rather than running year-round campaigns,

  - Create targeted educational resources for trending health topics, which attracts new members, increases retention, and generates revenue through insurance sales and corporate partnerships


### Business Impact Example

**Scenario:** The system shows "diabetes management" appears in 40% of articles, meaning many readers are interested in diabetes help.

**Action:** AARP creates diabetes guides, hosts diabetes workshops, and partners with companies to get member discounts on glucose monitors.

**Result:** Members with diabetes get practical help managing their condition, leading to happier members who stay with AARP longer and recommend it to others. This strengthens AARP's reputation as an organization that truly helps seniors with their health challenges.



## Setup Instructions

This section explains how to get the project running, either in a local Python environment or inside a Docker container. Before you begin, make sure you have valid API keys for both OpenAI and Groq, and store them in a `.env` file.

---

### 1. Local Setup

#### Prerequisites
- Python 3.9 or higher  
- [pip](https://pip.pypa.io/en/stable/) (Python package manager)  
- An OpenAI API key and a Groq API key (to be stored in `.env`)  

#### Steps
```bash
# 1. Clone the repository
git clone https://github.com/your-username/aarp-health-theme-cluster.git
cd aarp-health-theme-cluster

# 2. Create and activate a virtual environment
python -m venv env
source env/bin/activate      # On Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Update the .env file with your API keys
#    (a .env file is already present, so open it and add your keys)
#
#    Example .env contents:
#    OPENAI_API_KEY=your_openai_key_here
#    GROQ_API_KEY=your_groq_key_here

# 5. Run the main script to execute the entire pipeline
python main.py
```

> **Note:**  
> - `main.py` orchestrates all modules (scraper, cleaner, summarizer, cluster, etc.) in the correct sequence.  
> - Output files will be generated inside the `results/` directory:  
>   - `cluster_results.json`: shows, for each theme, the list of article links that belong to that cluster.  
>   - `document_keywords.json`: lists the major keywords that each article primarily discusses.
>   - `summaries.json`: summaries for each article    

---

### 2. Docker Setup

#### Prerequisites
- [Docker](https://www.docker.com/get-started) installed on your machine  

#### Steps
```bash
# 1. Clone the repository
git clone https://github.com/your-username/aarp-health-theme-cluster.git
cd aarp-health-theme-cluster

# 2. Update the .env file with your API keys
#    Example .env contents:
#    OPENAI_API_KEY=your_openai_key_here
#    GROQ_API_KEY=your_groq_key_here

# 3. Build the Docker image
docker build -t aarp-health-cluster .

# 4. Run the container, mounting a local 'results/' directory
docker run --env-file .env -v $(pwd)/results:/app/results aarp-health-cluster
```

> **Note:**  
> - The Docker container will read your OpenAI and Groq keys from the `.env` file.  
> - Any output files created inside the container (e.g., `cluster_results.json`, `document_keywords.json`) will be saved to the `results/` folder on your local machine.  
> - `cluster_results.json` shows, for each theme, the list of article links that belong to that cluster.  
> - `document_keywords.json` lists the major keywords that each article primarily discusses.
>   - `summaries.json`: summaries for each article 

---

With these instructions, anyone can set up and run the entire pipeline—either directly in a Python environment or via Docker—ensuring consistent outputs across different machines.




## Project Structure

Below is a breakdown of each file and folder in this repository, with a brief description of its role in the overall pipeline.

```
├── cleaner.py                 
│   └── Reads raw scraped articles (from `health_articles_depth_3.csv`), removes empty or invalid entries, and standardizes text for further processing.

├── cluster.py                 
│   └── Loads cleaned articles and their summaries, computes semantic similarity (via LLM embeddings), and groups articles into coherent theme clusters.  
│       • Outputs:  
│         – `article_to_theme.json` (mapping of article IDs to theme names)  
│         – `cluster_results.json` (human-readable JSON listing which article links belong to each theme)

├── document_keywords.json     
│   └── (Generated output) Contains a list of major keywords for each article, extracted during the clustering/tagging process. Helps verify that each article’s primary topics are correctly captured.

├── Dockerfile                 
│   └── Defines a Docker image that installs dependencies, copies code into the container, and runs the pipeline end to end when `docker run` is executed.

├── health_articles_depth_3.csv
│   └── (Raw scraped data) A CSV file generated by `scraper.py` that contains article IDs, titles, URLs, and full text for each AARP Health Channel article.

├── main.py                    
│   └── Orchestrates the entire pipeline in sequence (scraper → cleaner → summarizer → cluster).  
│       • When you run `python main.py`, it calls each module in the correct order and writes all output into `results/`.

├── requirements.txt           
│   └── Lists all Python packages required to run the project (e.g., beautifulsoup4, pandas, langchain, openai, groq).

├── scraper.py                 
│   └── Crawls the AARP Health Channel website, collects article titles, URLs, and content, and writes them to `health_articles_depth_3.csv`.

├── summarizer.py              
│   └── Loads cleaned articles, calls an LLM (via OpenAI + LangChain) to generate a concise summary for each article, and saves those summaries to `results/summaries.json`.

├── tagger.py                  
│   └── (Optional refinement step) Uses LLM prompts to assign or adjust theme labels for each cluster, ensuring labels accurately reflect article content.

├── utils.py                   
│   └── A collection of shared helper functions (e.g., reading/writing JSON, interacting with environment variables, wrapping LLM API calls) used by multiple modules.

├── article_to_theme.json      
│   └── (Generated output) A JSON file mapping each article ID (from `health_articles_depth_3.csv`) to its assigned theme name.

├── cluster_results.json       
│   └── (Generated output) A JSON file that, for each theme, lists the URLs of all articles belonging to that cluster. Useful for quick review and validation.

├── results/                   
│   ├── summaries.json         # Contains the LLM-generated summary for each article (article ID → summary text).  
│   ├── article_to_theme.json  # Copied here from top-level for easy access.  
│   ├── cluster_results.json   # Copied here from top-level for easy access.  
│   └── document_keywords.json # Copied here from top-level for easy access.  

└── .env                       
    └── Stores environment variables (not checked into version control), including:  
      • `OPENAI_API_KEY`  
      • `GROQ_API_KEY`  
```

Each module is designed to be self‐contained, allowing you to run individual steps in isolation or execute the entire workflow via `main.py`. Outputs are saved under `results/` for easy examination and downstream use.



