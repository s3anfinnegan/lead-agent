import os
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

# Configuration
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

client = Groq(api_key=GROQ_API_KEY)
tavily = TavilyClient(api_key=TAVILY_API_KEY)

def generate_search_queries():
    """Uses LLM to create 5 descriptive search strings for Tavily."""
    prompt = """Generate 5 distinct search queries to find LinkedIn profiles of professional 
    Asset Integrity Managers or Subsea Operations Managers in Offshore Wind and Aquaculture.
    Target regions: UK, USA, and Ireland.
    
    Example: 'LinkedIn profile Asset Integrity Manager Offshore Wind UK'
    
    Return ONLY the queries, one per line. Do not use 'site:' operators. 
    Do not include introductory text or numbers."""
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    lines = completion.choices[0].message.content.split('\n')
    # Clean the lines: remove numbers (like '1. ') and strip whitespace
    queries = []
    for line in lines:
        clean_line = line.strip()
        # Remove common list prefixes like '1. ' or '- '
        if clean_line and (clean_line[0].isdigit() or clean_line.startswith('-')):
            clean_line = clean_line.split(' ', 1)[-1]
        if clean_line:
            queries.append(clean_line)
            
    return queries[:5]
    """Uses LLM to create 5 distinct search strings, strictly formatted."""
    prompt = """Generate 5 distinct Google Search queries to find LinkedIn profiles of Asset Integrity Managers 
    or Subsea Operations Managers in Offshore Wind and Aquaculture in the UK, USA, and Ireland. 
    Format: site:linkedin.com/in/ "Job Title" "Industry" "Region"
    Return ONLY the queries, one per line. Do not include introductory text or numbers."""
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    # Filter out any empty lines or conversational filler
    lines = completion.choices[0].message.content.split('\n')
    return [line.strip() for line in lines if "site:linkedin.com" in line]

def score_lead(title, snippet):
    """Uses the 3.3 70B model to evaluate the 'Need' level."""
    prompt = f"""
    On a scale of 1-5, how much would this person need a low-cost, man-portable AUV for inspections?
    Title: {title}
    Bio/Snippet: {snippet}
    
    1: Not relevant
    5: High priority (direct decision maker for offshore costs)
    Return ONLY the number.
    """
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile", # <--- UPDATED MODEL ID
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error scoring lead: {e}")
        return "N/A"

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