import os
import requests
import re
import base64
import sys
import datetime

def generate_bar(percent, width=20):
    filled_len = int(width * percent / 100)
    bar = "⣿" * filled_len + "⣀" * (width - filled_len)
    return bar

def get_days_active():
    start_date = datetime.date(2024, 8, 15) 
    current_date = datetime.date.today()
    delta = current_date - start_date
    return f"{delta.days:03d}"

def update_readme():
    api_key = os.getenv("WAKATIME_API_KEY")
    if not api_key:
        sys.exit(1)
        
    GOAL_HOURS = 500
    
    url = "https://wakatime.com/api/v1/users/current/stats/all_time"
    auth_header = base64.b64encode(api_key.encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", {})
    except Exception:
        sys.exit(1)

    languages_data = data.get("languages", [])
    if not languages_data:
        sys.exit(0)
    
    blacklist = {
        "html", "html5", "css", "scss", "sass", "less", "postcss", "svg", "xml",
        "json", "yaml", "yml", "toml", "ini", "csv", "graphql", "properties", 
        "markdown", "md", "text", "plain text", "txt", "git config", "git", "ignore list",
        "ejs", "jinja", "twig", "pug", "handlebars", "mustache", "blade", "blade template", "liquid", "smarty", "erb", "hbs"
    }
    
    filtered_languages = []
    other_seconds = 0
    
    for lang in languages_data:
        name = lang.get("name", "")
        name_lower = name.lower()
        is_other = (
            name_lower in blacklist 
            or "template" in name_lower
            or "config" in name_lower
        )
        if is_other:
            other_seconds += lang.get("total_seconds", 0)
        else:
            filtered_languages.append(lang)
            
    if other_seconds > 0:
        filtered_languages.append({
            "name": "Other",
            "total_seconds": other_seconds
        })
        
    filtered_languages.sort(key=lambda x: x.get("total_seconds", 0), reverse=True)
    
    days_active = get_days_active()
    header_art = f"Day: {days_active}"

    waka_stats = ""
    for lang in filtered_languages[:5]:
        name = lang["name"].ljust(18)
        total_seconds = lang.get("total_seconds", 0)
        hours = total_seconds / 3600
        
        hrs_val = int(hours)
        mins_val = int((hours % 1) * 60)
        time_str = f"{hrs_val} hrs {mins_val} mins".ljust(20)
        
        percent = (hours / GOAL_HOURS) * 100
        if percent > 100: percent = 100
        
        bar = generate_bar(percent)
        percent_str = f"{percent:05.2f} %"
        
        waka_stats += f"{name} {time_str} {bar}   {percent_str}\n"

    final_content = f"{header_art}\n\n{waka_stats}"

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme = f.read()
            
        pattern = r"<!--START_SECTION:waka-->.*?<!--END_SECTION:waka-->"
        replacement = f"<!--START_SECTION:waka-->\n\n```txt\n{final_content}```\n\n<!--END_SECTION:waka-->"
        
        new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    update_readme()
