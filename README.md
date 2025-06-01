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

Below is a high-level view of every file and folder in this repository:

```
├── cleaner.py
├── cluster.py
├── Dockerfile
├── main.py
├── requirements.txt
├── scraper.py
├── summarizer.py
├── tagger.py
├── utils.py
├── results/
│   ├── summaries.json
│   ├── article_to_theme.json
│   ├── cluster_results.json
│   └── document_keywords.json
└── .env
```
Each entry corresponds to a module or output used by the pipeline.  

### Methodology

### Block diagram


![Pipeline Block Diagram](images/block-diagram.png)

*Figure 1: High-level pipeline showing each module and its data flow.*

Below is a detailed, step-by-step description of each stage. We begin with the **Web Scraper**, which crawls the AARP Health Channel to gather every article URL and its full content.

---

### 1. Web Scraper (`scraper.py`)

- **Purpose:** Crawl the AARP Health Channel and collect every article’s URL and full text.

- **How It Works:**

    The web scraper begins at a specified base URL (e.g., `https://www.aarp.org/health`) and uses a recursive function, `extract_article_Links(base_url, max_depth)`, to follow only those links whose path starts with `/health/`, up to a defined depth. By issuing HTTP requests and parsing each page with BeautifulSoup, it builds a set of valid article URLs and writes them to `links.txt`. Next, for each URL in this set (or from the existing `links.txt`), the helper function `get_content_from_link(link, df)` fetches the page, locates the `<div class="articlecontentfragment">` element, concatenates its text, cleans whitespace, and appends the result as `[link, full_text]` to a pandas DataFrame. Finally, the orchestrator function `extract_article_content(base_link)` combines these steps—calling `extract_article_Links`, reading or updating `links.txt`, iterating through each URL with `get_content_from_link`, and saving the completed DataFrame to `results/health_articles_depth_3.csv` (columns: `Link` and `Content`).

  <!-- 1. **`extract_article_Links(base_url, max_depth)`**  
     - Starts at `base_url` (e.g., `https://www.aarp.org/health`).  
     - Recursively follows only links whose path begins with `/health/`, up to a specified `max_depth`. This `depth` parameter limits how many levels of internal `/health/...` pages are crawled.  
     - Uses `requests.get()` and `BeautifulSoup` to parse each page.  
     - Collects every valid `/health/...` URL into a set and saves them to `links.txt`.

  2. **`get_content_from_link(link, df)`**  
     - Fetches the given article URL.  
     - Looks for `<div class="articlecontentfragment">`.  
     - Extracts and concatenates the text inside that div.  
     - Cleans whitespace and adds one row `[link, full_text]` to a pandas DataFrame.

  3. **`extract_article_content(base_link)`**  
     - Calls `extract_article_Links(base_link, max_depth=3)` (or whatever depth you choose) to build a list of candidate URLs.  
     - Reads from `links.txt` (if present) or uses the returned set.  
     - Iterates over each URL, invoking `get_content_from_link` to gather full text.  
     - Saves the final DataFrame (columns: `Link`, `Content`) to `results/health_articles_depth_3.csv`. -->

- **Output:**  
  A CSV file at `results/health_articles_depth_3.csv` containing every scraped article’s URL and its cleaned, full-text content.  

