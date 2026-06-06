import os
import requests
import re
import base64
import sys

def generate_bar(percent, width=20):
    # BLOCKS: ⣀⣄⣤⣦⣶⣷⣿
    filled_len = int(width * percent / 100)
    bar = "⣿" * filled_len + "⣀" * (width - filled_len)
    return bar

def update_readme():
    api_key = os.getenv("WAKATIME_API_KEY")
    if not api_key:
        print("Error: WAKATIME_API_KEY not found in environment variables.")
        sys.exit(1)
        
    # Target hours for 100%
    GOAL_HOURS = 8766
    
    print("Fetching WakaTime stats...")
    url = "https://wakatime.com/api/v1/users/current/stats/all_time"
    auth_header = base64.b64encode(api_key.encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}"}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", {})
    except Exception as e:
        print(f"Error fetching WakaTime stats: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        sys.exit(1)

    languages = data.get("languages", [])
    if not languages:
        print("No language data found.")
        # Optional: Don't exit if we just want to keep old stats, 
        # but here we'll exit to show there's an issue
        sys.exit(0)
    
    waka_content = "```txt\n"
    for lang in languages[:5]: # Top 5 languages
        name = lang["name"].ljust(18)
        total_seconds = lang.get("total_seconds", 0)
        hours = total_seconds / 3600
        
        hrs_val = int(hours)
        mins_val = int((hours % 1) * 60)
        time_str = f"{hrs_val} hrs {mins_val} mins".ljust(20)
        
        # Calculate percentage based on 8766 hours goal
        percent = (hours / GOAL_HOURS) * 100
        if percent > 100: percent = 100
        
        bar = generate_bar(percent)
        percent_str = f"{percent:05.2f} %"
        
        waka_content += f"{name} {time_str} {bar}   {percent_str}\n"
    waka_content += "```"

    print("Updating README.md...")
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            readme = f.read()

        pattern = r"<!--START_SECTION:waka-->.*?<!--END_SECTION:waka-->"
        if not re.search(pattern, readme, flags=re.DOTALL):
            print("Error: Waka section tags not found in README.md")
            sys.exit(1)
            
        replacement = f"<!--START_SECTION:waka-->\n\n{waka_content}\n\n<!--END_SECTION:waka-->"
        new_readme = re.sub(pattern, replacement, readme, flags=re.DOTALL)
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_readme)
        print("README.md updated successfully.")
    except Exception as e:
        print(f"Error updating README: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_readme()
