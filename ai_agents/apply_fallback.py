import glob
import os
import re

search_path = r"C:\projects\commercepulse\AZURE\ai_agents\app\agents\nodes\*.py"
files = glob.glob(search_path)
files.append(r"C:\projects\commercepulse\AZURE\ai_agents\main.py")

for file in files:
    if not os.path.isfile(file):
        continue
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern 1: api_key=get_groq_api_key()
    old_str_1 = 'ChatGroq(api_key=get_groq_api_key(), model="llama3-8b-8192", temperature=0.0)'
    new_str_1 = 'ChatGroq(api_key=get_groq_api_key(), model="llama-3.3-70b-versatile", temperature=0.0).with_fallbacks([ChatGroq(api_key=get_groq_api_key(), model="llama3-8b-8192", temperature=0.0)])'
    
    # Pattern 2: api_key=key
    old_str_2 = 'ChatGroq(api_key=key, model="llama3-8b-8192", temperature=0.0)'
    new_str_2 = 'ChatGroq(api_key=key, model="llama-3.3-70b-versatile", temperature=0.0).with_fallbacks([ChatGroq(api_key=key, model="llama3-8b-8192", temperature=0.0)])'
    
    # Pattern 3: without explicit temperature if it exists?
    # I'll just do regex replacement for the model name to be safe
    # Wait, simple string replacement is safer.
    
    new_content = content.replace(old_str_1, new_str_1).replace(old_str_2, new_str_2)
    
    if new_content != content:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {os.path.basename(file)}")

print("Done.")
