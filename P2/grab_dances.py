import os
import re
import requests

BASE_URL = "https://www.ottawaenglishdance.org/playford/doku.php"
INDEX_URL = f"{BASE_URL}?id=english_dance_instructions_index&do=export_raw"
OUTPUT_DIR = "./dances"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_raw_text(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_dance_ids(text):
    return re.findall(r"\[\[\s*(ins_[^\s\|\]]+)", text)

def save_dance_file(dance_id, content):
    file_path = os.path.join(OUTPUT_DIR, f"{dance_id}.txt")
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Saved: {file_path}")

def main(): 
    print("Fetching index page...")
    index_text = get_raw_text(INDEX_URL)
    print("Extracting dance IDs...")
    dance_ids = extract_dance_ids(index_text)
    print(f"Found {len(dance_ids)} dances.")
    for dance_id in dance_ids:
        dance_url = f"{BASE_URL}?id={dance_id}&do=export_raw"
        print(f"Fetching {dance_id}...")
        try:
            dance_text = get_raw_text(dance_url)
            save_dance_file(dance_id, dance_text)
        except requests.RequestException as e:
            print(f"Failed to fetch {dance_id}: {e}")

if __name__ == "__main__":
    main()
