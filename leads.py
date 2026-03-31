import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

# Configuration Variables - Change these to pivot your search!
TARGET_ROLES = "Asset Integrity Managers or Subsea Operations Managers"
INDUSTRIES = "Offshore Wind and Aquaculture"
REGIONS = "UK, USA, and Ireland"
PROJECT_DESC = "A low-cost, man-portable AUV that works in swarms for inspections of hulls, cables, and wind farms to reduce vessel costs."

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def load_prompt(filename, replacements):
    """Reads a markdown prompt and injects variables."""
    path = os.path.join("prompts", filename)
    with open(path, "r") as f:
        prompt = f.read()
    for key, value in replacements.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)
    return prompt

def generate_search_queries():
    prompt = load_prompt("generate-leads.md", {
        "target_roles": TARGET_ROLES,
        "industries": INDUSTRIES,
        "regions": REGIONS
    })
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    lines = completion.choices[0].message.content.split('\n')
    return [line.strip() for line in lines if line.strip()][:5]

def score_lead(title, snippet):
    prompt = load_prompt("score-leads.md", {
        "project_description": PROJECT_DESC,
        "title": title,
        "snippet": snippet
    })
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error scoring lead: {e}")
        return "N/A"

def main():
    print("🚀 Starting Modular Discovery Agent...")
    queries = generate_search_queries()
    leads_list = []

    for query in queries:
        print(f"Searching: {query}")
        search_results = tavily.search(query=query, search_depth="advanced", max_results=10)
        
        for res in search_results['results']:
            need_score = score_lead(res['title'], res['content'])
            leads_list.append({
                "Industry": INDUSTRIES,
                "Name": res['title'].split('|')[0].strip(),
                "LinkedIn Job Title": res['title'],
                "Need": need_score,
                "URL": res['url']
            })

    df = pd.DataFrame(leads_list)
    df.to_csv("leads.csv", index=False)
    print("✅ Done! Results saved to leads.csv")

if __name__ == "__main__":
    main()