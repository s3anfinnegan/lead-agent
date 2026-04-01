import os
import json
import pandas as pd
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

def load_config():
    """Loads search parameters from config.json."""
    with open("config.json", "r") as f:
        return json.load(f)

CONFIG = load_config()

# Now we access variables via the CONFIG dictionary
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def load_prompt(filename, replacements):
    path = os.path.join("prompts", filename)
    with open(path, "r") as f:
        prompt = f.read()
    for key, value in replacements.items():
        prompt = prompt.replace(f"{{{{{key}}}}}", value)
    return prompt

def generate_search_queries():
    # Using CONFIG values
    prompt = load_prompt("generate-leads.md", {
        "target_roles": CONFIG["target_roles"],
        "industries": CONFIG["industries"],
        "regions": CONFIG["regions"]
    })
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    
    lines = completion.choices[0].message.content.split('\n')
    return [line.strip() for line in lines if line.strip() and "site:" not in line][:5]

def score_lead(title, snippet):
    # Using CONFIG values
    prompt = load_prompt("score-leads.md", {
        "project_description": CONFIG["project_desc"],
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

def generate_html_dashboard(df):
    headers = "".join([f"<th>{col}</th>" for col in df.columns])
    table_rows = ""
    for _, row in df.iterrows():
        table_rows += "<tr>"
        for col in df.columns:
            value = row[col]
            if "http" in str(value):
                table_rows += f'<td><a href="{value}" target="_blank" class="btn btn-sm btn-primary">View Profile</a></td>'
            elif col == "Need":
                score = pd.to_numeric(value, errors='coerce')
                badge_class = "bg-danger" if score >= 4 else "bg-warning text-dark" if score == 3 else "bg-secondary"
                table_rows += f'<td><span class="badge {badge_class}">{value}/5</span></td>'
            else:
                table_rows += f"<td>{value}</td>"
        table_rows += "</tr>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Lead Discovery Dashboard</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f4f7f6; padding: 40px; }}
            .container {{ background: white; padding: 30px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
            .header-div {{ border-bottom: 3px solid #0d6efd; margin-bottom: 30px; padding-bottom: 15px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header-div">
                <h1>🚀 Lead Discovery Dashboard</h1>
                <p class="text-muted"><strong>Target:</strong> {CONFIG['target_roles']} | <strong>Industries:</strong> {CONFIG['industries']}</p>
            </div>
            <table class="table table-hover">
                <thead class="table-dark"><tr>{headers}</tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
    </body>
    </html>
    """
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write(html_content)

def main():
    print("🚀 Starting Config-Driven Discovery Agent...")
    queries = generate_search_queries()
    leads_list = []
    target_count = CONFIG.get("target_count", 10)

    for query in queries:
        if len(leads_list) >= target_count: break
        print(f"Searching: {query}")
        search_results = tavily.search(query=query, search_depth="advanced", max_results=20)
        
        for res in search_results['results']:
            if "linkedin.com/in/" in res['url']:
                need_score = score_lead(res['title'], res['content'])
                leads_list.append({
                    "Industry": CONFIG["industries"],
                    "Name": res['title'].split('|')[0].strip(),
                    "LinkedIn Job Title": res['title'],
                    "Need": need_score,
                    "URL": res['url']
                })
                if len(leads_list) >= target_count: break

    df = pd.DataFrame(leads_list)
    if not df.empty:
        df['Need'] = pd.to_numeric(df['Need'], errors='coerce')
        df = df.sort_values(by="Need", ascending=False)
        df.to_csv("leads.csv", index=False)
        generate_html_dashboard(df)
        print("✅ Dashboard generated: dashboard.html")

if __name__ == "__main__":
    main()