import os
import pandas as pd
from groq import Groq
from tavily import TavilyClient

# Configuration
GROQ_API_KEY = "your_groq_key_here"
TAVILY_API_KEY = "your_tavily_key_here"

client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def generate_search_queries():
    """Uses LLM to create 5 distinct search strings."""
    prompt = """Generate 5 Google Search queries to find LinkedIn profiles of Asset Integrity Managers 
    or Subsea Operations Managers in Offshore Wind and Aquaculture in the UK, USA, and Ireland. 
    Format: site:linkedin.com/in/ "Job Title" "Industry" "Region" """
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    # Simple split (assuming LLM returns a list)
    return completion.choices[0].message.content.split('\n')

def score_lead(title, snippet):
    """Uses the 70B model to evaluate the 'Need' level."""
    prompt = f"""
    On a scale of 1-5, how much would this person need a low-cost, man-portable AUV for inspections?
    Title: {title}
    Bio/Snippet: {snippet}
    
    1: Not relevant
    5: High priority (direct decision maker for offshore costs)
    Return ONLY the number.
    """
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return completion.choices[0].message.content.strip()

def main():
    print("🚀 Starting Customer Discovery Agent...")
    queries = generate_search_queries()
    leads_list = []

    for query in queries:
        if not query.strip(): continue
        print(f"Searching: {query}")
        # Search via Tavily
        search_results = tavily.search(query=query, search_depth="advanced", max_results=10)
        
        for res in search_results['results']:
            # Evaluate the lead
            need_score = score_lead(res['title'], res['content'])
            
            leads_list.append({
                "Industry": "Marine/Offshore", # Simplified for now
                "Name": res['title'].split('|')[0].strip(), # Basic cleaning
                "LinkedIn Job Title": res['title'],
                "Need": need_score,
                "URL": res['url']
            })

    # Save to CSV
    df = pd.DataFrame(leads_list)
    df.to_csv("leads.csv", index=False)
    print("✅ Leads list generated: leads.csv")

if __name__ == "__main__":
    main()