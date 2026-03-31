# AI-Powered Lead Generation Agent

A modular, LLM-driven search agent designed to identify, extract, and prioritize high-value leads from LinkedIn. Instead of traditional scraping, this agent uses search engine intelligence to find profiles and an LLM "reasoning" layer to score them based on specific project needs.

---

## 🚀 How It Works

The agent follows a three-stage autonomous workflow to transform a broad "Ideal Customer Profile" into a prioritized outreach list.

### 1. Template-Based Query Generation (Llama 3.1 8B)
The agent uses a modular prompt template (`prompts/generate-leads.md`) to generate optimized search strings.
* **Modularity:** Target roles, industries, and regions are injected into the template, making the agent easy to pivot to new markets.
* **Natural Language Search:** Optimized for the Tavily API to find high-relevance LinkedIn profiles without the brittleness of manual Boolean strings.

### 2. Live Search & LinkedIn Verification (Tavily API)
The agent executes the generated queries and performs a strict validation check.
* **Strict Filtering:** It automatically discards company pages, news articles, and job postings, ensuring only **personal LinkedIn profile URLs** (`/in/`) make it to the final list.
* **Dynamic Scaling:** The agent continues searching across multiple query variations until it reaches the desired number of verified leads.

### 3. Intelligence & Scoring (Llama 3.3 70B)
Extracted snippets are analyzed by **Llama 3.3 70B** for qualitative fit.
* **Custom Scoring Logic:** Using `prompts/score-leads.md`, the agent assigns a 1-5 "Need Score" based on the lead's seniority and relevance to the project description.
* **Prioritization:** The final output is automatically sorted, placing the highest-value prospects at the top of the file.

---

## 🛠️ Setup & Installation

### Prerequisites
* **Python 3.10+**
* **Groq API Key** (Using Llama 3.1 8B and Llama 3.3 70B)
* **Tavily API Key** (For search capabilities)

### Installation
1.  **Clone and Enter Directory:**
    ```bash
    git clone [https://github.com/yourusername/lead-gen-agent.git](https://github.com/yourusername/lead-gen-agent.git)
    cd lead-gen-agent
    ```

2.  **Set Up Environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    source venv/bin/activate # Mac/Linux
    pip install groq tavily-python pandas python-dotenv
    ```

3.  **Configure API Keys:**
    Create a `.env` file in the root directory:
    ```text
    GROQ_API_KEY=your_key_here
    TAVILY_API_KEY=your_key_here
    ```

---

## 📂 Project Structure
* `leads.py`: The core logic for searching, filtering, and scoring.
* `prompts/generate-leads.md`: Template for search query generation.
* `prompts/score-leads.md`: Template for AI lead evaluation.
* `.env`: Storage for API keys.

---

## 📊 Data Output
The agent generates a `leads.csv` with the following columns:

| Column | Description |
| :--- | :--- |
| **Industry** | The target sector defined in the config. |
| **Name** | Extracted name from the LinkedIn profile. |
| **LinkedIn Job Title** | The full professional headline. |
| **Need (1-5)** | AI-calculated priority score based on project fit. |
| **URL** | Verified LinkedIn personal profile link. |

---

> **Note:** This tool is designed for landing customer discovery calls, not for spamming. 