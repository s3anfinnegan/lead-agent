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
    print("🚀 Starting LinkedIn-Only Discovery Agent...")
    queries = generate_search_queries()
    leads_list = []
    target_count = 10  # We only want the top 10 verified LinkedIn leads

    for query in queries:
        if len(leads_list) >= target_count:
            break
            
        print(f"Searching: {query}")
        # We search for more than 10 to ensure we have enough to filter
        search_results = tavily.search(query=query, search_depth="advanced", max_results=20)
        
        for res in search_results['results']:
            url = res['url']
            
            # STRICT FILTER: Only proceed if it is a LinkedIn Personal Profile
            if "linkedin.com/in/" in url:
                print(f"Found Verified Lead: {res['title']}")
                
                need_score = score_lead(res['title'], res['content'])
                
                leads_list.append({
                    "Industry": INDUSTRIES,
                    "Name": res['title'].split('|')[0].strip(),
                    "LinkedIn Job Title": res['title'],
                    "Need": need_score,
                    "URL": url
                })
                
                # Check if we hit our 10-lead goal
                if len(leads_list) >= target_count:
                    break
            else:
                # Skip company pages, news articles, etc.
                continue

    # Create the DataFrame and sort by 'Need' so the best leads are at the top
    df = pd.DataFrame(leads_list)
    if not df.empty:
        df['Need'] = pd.to_numeric(df['Need'], errors='coerce')
        df = df.sort_values(by="Need", ascending=False)
        
    df.to_csv("leads.csv", index=False)
    print(f"✅ Done! {len(leads_list)} verified LinkedIn leads saved to leads.csv")

if __name__ == "__main__":
    main()