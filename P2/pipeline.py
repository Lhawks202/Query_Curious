import os
import re
import json
import random
from openai import OpenAI
from dotenv import load_dotenv

# === Config ===
DANCE_DIR = "dances"
OUTPUT_DIR = "output"
PROMPT_DIR = "prompts"
MODEL = "gpt-4o-mini"
CHUNK_THRESHOLD = 20       # Max figures per merge batch

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === OpenAI Client ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# === Helper Functions ===
def load_prompt_template(filename):
    path = os.path.join(PROMPT_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def extract_code_block(text):
    match = re.search(r"<code>(.*?)</code>", text, re.DOTALL)
    return match.group(1) if match else None

def run_openai_prompt(messages):
    resp = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        response_format={"type": "json_object"}
    )
    return json.loads(resp.choices[0].message.content)

# === Stage 1: Independent Extraction ===
def build_simple_prompt_for_figures(code_block):
    system_prompt = load_prompt_template("extract_figures.txt")
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"<code>{code_block}</code>"}
    ]

def extract_figures_independent():
    all_raw = []
    for fname in os.listdir(DANCE_DIR):
        if not fname.endswith(".txt"):
            continue
        text = open(os.path.join(DANCE_DIR, fname), encoding="utf-8").read()
        block = extract_code_block(text)
        if not block:
            continue
        messages = build_simple_prompt_for_figures(block)
        result = run_openai_prompt(messages)
        all_raw.extend(result.get("figures", []))
    out_path = os.path.join(OUTPUT_DIR, "all_raw_figures.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_raw, f, indent=2)
    print(f"Extracted {len(all_raw)} raw figures → {out_path}")

# === Stage 2: Recursive Divide‐and‐Conquer Merge ===
def merge_two_figure_lists(list1, list2):
    system_prompt = load_prompt_template("merge_figures.txt")
    content = (
        "\nList1:\n" + json.dumps(list1, indent=2)
        + "\nList2:\n" + json.dumps(list2, indent=2)
    )
    messages = [
        {"role":"system", "content": system_prompt},
        {"role":"user",   "content": content}
    ]
    print("1: ", len(list1))
    print("2: ", len(list2))
    result = run_openai_prompt(messages)
    print("R: ", len(result.get("figures", [])))
    return result.get("figures", [])

def chunk_list(figures, size=CHUNK_THRESHOLD):
    """Split a list into sublists of at most `size` items each."""
    return [figures[i : i + size] for i in range(0, len(figures), size)]

def dedupe_figures():
    raw_path = os.path.join(OUTPUT_DIR, "all_raw_figures.json")
    all_raw = json.load(open(raw_path, encoding="utf-8"))
    print(f"Total raw figures: {len(all_raw)}")

    current_figures = all_raw
    pass_num = 0

    try:
        while True:
            pass_num += 1
            print(f"\nMerge pass {pass_num}: {len(current_figures)} figures")

            random.shuffle(current_figures)
            chunks = chunk_list(current_figures, CHUNK_THRESHOLD)
            print(f" → Created {len(chunks)} random chunks")

            new_chunks = []
            found_duplicates = False
            i = 0
            while i < len(chunks):
                if i + 1 < len(chunks):
                    a, b = chunks[i], chunks[i+1]
                    merged = merge_two_figure_lists(a, b)

                    if len(merged) < len(a) + len(b):
                        found_duplicates = True

                    new_chunks.append(merged)
                    i += 2
                else:
                    new_chunks.append(chunks[i])
                    i += 1

            current_figures = [fig for chunk in new_chunks for fig in chunk]
            print(f" → Figures after pass: {len(current_figures)} (duplicates found? {found_duplicates})")

            if not found_duplicates:
                break

    except Exception as e:
        print("X Deduplication interrupted due to error:", e)
        temp_path = os.path.join(OUTPUT_DIR, "temp_dedupe_figures.json")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(current_figures, f, indent=2)
        print(f"Saved partial progress to {temp_path}")
        return  # Exit early

    final_by_name = {fig["name"]: fig for fig in current_figures}
    final_library = list(final_by_name.values())
    print(f"\nFinal unique figures: {len(final_library)}")

    lib_path = os.path.join(OUTPUT_DIR, "figure_library.json")
    with open(lib_path, "w", encoding="utf-8") as f:
        json.dump(final_library, f, indent=2)
    print(f"Saved deduplicated library → {lib_path}")

# === Stage 3: Generate Dance Definitions with Video Link & Name ===

def extract_video_link(text):
    """
    Look for the first YouTube URL (youtu.be or youtube.com/watch?v=)
    anywhere in the text. Returns None if none found.
    """
    pattern = re.compile(
        r'(https?://(?:www\.)?youtu(?:\.be/|be\.com/watch\?v=)[A-Za-z0-9_\-]+)'
    )
    m = pattern.search(text)
    return m.group(1) if m else None

def build_prompt_for_dance(code_block, library):
    system_prompt = load_prompt_template("define_dances.txt")
    return [
        {"role": "system",  "content": system_prompt},
        {"role": "user",    "content": "\nFigures:\n" + json.dumps(library, indent=2) + f"\n\n<code>{code_block}</code>"},
    ]

def generate_dances():
    # load your deduped figure library
    lib_path = os.path.join(OUTPUT_DIR, "figure_library.json")
    library = json.load(open(lib_path, encoding="utf-8"))

    for fname in os.listdir(DANCE_DIR):
        if not fname.endswith(".txt"):
            continue

        raw_path = os.path.join(DANCE_DIR, fname)
        text     = open(raw_path, encoding="utf-8").read()

        # 1) pull out the <code> block for choreography
        code_block = extract_code_block(text)
        if not code_block:
            print(f"No <code> block in {fname}, skipping.")
            continue

        # 2) ask GPT for the JSON dance_definition
        messages = build_prompt_for_dance(code_block, library)
        result   = run_openai_prompt(messages)
        dance_def = result.get("dance_definition", {})

        # 3) scrape any YouTube link in the raw text
        video = extract_video_link(text)
        if video:
            dance_def["video"] = video

        # 4) record the dance name as the filename (no extension)
        dance_def["name"] = os.path.splitext(fname)[0]

        # 5) write out the enriched JSON
        out_fn  = fname.replace(".txt", ".json")
        out_path = os.path.join(OUTPUT_DIR, out_fn)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(dance_def, f, indent=2)

        print(f"Wrote → {out_path} (video: {video or 'none'})")

def main():
    # extract_figures_independent()
    dedupe_figures()
    generate_dances()

if __name__ == "__main__":
    main()
