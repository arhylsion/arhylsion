import os
import requests
import re
import base64
import sys

def generate_bar(percent, width=20):
    filled_len = int(width * percent / 100)
    bar = "⣿" * filled_len + "⣀" * (width - filled_len)
    return bar

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
    
    waka_content = "```txt\n"
    for lang in languages_data[:5]:
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
        
        waka_content += f"{name} {time_str} {bar}   {percent_str}\n"
    waka_content += "```"

    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme = f.read()
        pattern = r"<!--START_SECTION:waka-->.*?<!--END_SECTION:waka-->"
        replacement = f"<!--START_SECTION:waka-->\n\n{waka_content}\n\n<!--END_SECTION:waka-->"
        new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
    except Exception:
        sys.exit(1)

if __name__ == "__main__":
    update_readme()
