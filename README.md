# AI-Powered Lead Generation Agent

A modular, LLM-driven search agent designed to identify, extract, and prioritise high-value leads from LinkedIn using real-time search data. Instead of traditional scraping, this agent uses search engine intelligence to find profiles and an LLM "reasoning" layer to score them based on specific needs.

---

## 🚀 How It Works

The agent follows a three-stage autonomous workflow to transform a broad "Ideal Customer Profile" into a prioritised outreach list.

### 1. Query Generation (Llama 3.1 8B)
The agent takes a high-level description of a target persona and uses **Llama 3.1 8B** to generate a series of optimised "Google Dorking" strings. 
* **Method:** It targets `site:linkedin.com/in/` combined with specific industry keywords, seniority levels, and geographic regions.
* **Benefit:** This creates a much wider net than a single manual search.

### 2. Live Search & Extraction (Tavily API)
The agent executes the generated queries via the **Tavily Search API**. 
* **Method:** It bypasses the need for a browser-based scraper by pulling data directly from search engine indices. 
* **Data Captured:** It extracts the profile Name, LinkedIn Job Title, URL, and a text "snippet" from the search result.

### 3. Intelligence & Scoring (Llama 3.1 70B)
The extracted snippets are passed to a larger model (**Llama 3.1 70B**) for qualitative analysis.
* **Industry Mapping:** Categorises the lead based on the context found in their profile snippet.
* **Need Scoring (1-5):** The model performs "zero-shot" reasoning to determine how likely this person is to experience the specific pain points you are solving.
* **Output:** The agent compiles everything into a structured `.csv` file ready for your CRM or outreach tool.

---

## 🛠️ Setup & Installation

### Prerequisites
* **Python 3.10+**
* **Groq API Key** (For Llama 3.1 models)
* **Tavily API Key** (For search capabilities)

### Installation
1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/yourusername/lead-gen-agent.git](https://github.com/yourusername/lead-gen-agent.git)
    cd lead-gen-agent
    ```

2.  **Create a Virtual Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Mac/Linux
    ```

3.  **Install Dependencies:**
    ```bash
    pip install groq tavily-python pandas
    ```

---

## 📊 Data Output
The agent generates a `leads.csv` with the following columns:

| Column | Description |
| :--- | :--- |
| **Industry** | The sector the lead operates in. |
| **Name** | Extracted name from the profile. |
| **LinkedIn Job Title** | The full title listed
