import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# === Config ===
MAX_FILES = float('inf')
INCREMENTAL_THRESHOLD = 20
DANCE_DIR = "dances"
OUTPUT_DIR = "output"
PROMPT_DIR = "prompts"
MODEL = "gpt-4o-mini"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === OpenAI Client ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# === Local Figure Dictionary ===
local_figure_dict = []

# === Few-Shot Example Data and Expected Output ===
THE_ADIEU_EXAMPLE = """
Dance Name: The Adieu
<code>
A        Partners face, balance back & cross R sh, 
         balance back & cross L sh, then all
         face down & take R h:
B        All lead down, turn Women under arms, lead up, 
         C1 & C3 cast a place to finish on centre line of set, 
         Men below partners and back to back with them; 
         take hands 3 at top & bottom, but hands 4 in middle:
C        All set R & L, then circle L, breaking to finish with 
         partners facing in 1st progressed place; all set R & L:
D        Partners take Rh & 'overhead Allemande' W1 moves forward 
         & back as Man gypsies clockwise round her, she passing 
         under joined R hands); C1 & C3 cast again as others L h 
         overhead Allemande, moving up.
</code>
"""

EXPECTED_JSON_OUTPUT = {
  "figures": [
    {
      "name": "Balance and Cross Right Shoulder",
      "roles": "Partners",
      "start_position": "Facing partner across the set",
      "action": "Balance back; cross passing right shoulder",
      "end_position": "Swapped sides of set, facing partner",
      "duration": 4
    },
    {
      "name": "Balance and Cross Left Shoulder",
      "roles": "Partners",
      "start_position": "Facing partner",
      "action": "Balance back; cross passing left shoulder",
      "end_position": "Returned to original side",
      "duration": 4
    },
    # ... other figures
  ],
  "dance_definition": {
    "title": "The Adieu",
    "source": "Thompson Compleat vol IV (1780)",
    "music_structure": "A B C D",
    "formation": "Triple minor longways",
    "phrases": {
      "A": [
        "Balance and Cross Right Shoulder",
        "Balance and Cross Left Shoulder",
        "Face Down and Take Right Hands"
      ],
      "B": [
        "Lead Down and Up with Turn Under",
        "Cast and Form Center Line",
        "Take Hands in Groups"
      ],
      "C": [
        "Set and Circle Left"
      ],
      "D": [
        "Overhead Allemande Right",
        "Final Cast and Left-Hand Allemande"
      ]
    }
  }
}

# === Helper Function to Load a Prompt Template ===
def load_prompt_template(template_filename):
    """Read the prompt template from a file in the prompt directory."""
    template_path = os.path.join(PROMPT_DIR, template_filename)
    with open(template_path, "r", encoding="utf-8") as f:
        return f.read()

# === Updated Functions for Building Prompts ===
def build_prompt_for_figures(code_block, figure_dict):
    """Build a prompt from a template to extract or update figures."""
    template = load_prompt_template("extract_figures.txt")
    prompt_str = template.format(
        THE_ADIEU_EXAMPLE=THE_ADIEU_EXAMPLE,
        figures_json=json.dumps(EXPECTED_JSON_OUTPUT["figures"], indent=2),
        figure_dict_content=json.dumps(figure_dict, indent=2)
    )
    return [
        {"role": "system", "content": prompt_str},
        {"role": "user", "content": f"Extract and match figures from this dance:\n<code>{code_block}</code>"}
    ]

def build_prompt_for_dance(code_block, figure_dict):
    """Build a prompt from a template to convert a dance using known figures."""
    template = load_prompt_template("define_dances.txt")
    prompt_str = template.format(
        THE_ADIEU_EXAMPLE=THE_ADIEU_EXAMPLE,
        figures_json=json.dumps(EXPECTED_JSON_OUTPUT["figures"], indent=2),
        dance_definition_json=json.dumps(EXPECTED_JSON_OUTPUT["dance_definition"], indent=2),
        figure_dict_content=json.dumps(figure_dict, indent=2)
    )
    return [
        {"role": "system", "content": prompt_str},
        {"role": "user", "content": f"Convert this dance into a definition using only known figures:\n<code>{code_block}</code>"}
    ]

def extract_code_block(text):
    """Extracts all content between <code>...</code> tags."""
    match = re.search(r"<code>(.*?)</code>", text, re.DOTALL)
    if match:
        return match.group(1)
    return None

def run_openai_prompt(prompt):
    """Send a prompt to OpenAI and return the JSON response."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=prompt,
        response_format={"type": "json_object"}
    )
    return json.loads(response.choices[0].message.content)

def save_figure_dict():
    """Incrementally offload the figure dictionary to a file."""
    figure_dict_path = os.path.join(OUTPUT_DIR, "figure_library.json")
    with open(figure_dict_path, "w", encoding="utf-8") as f:
        json.dump(local_figure_dict, f, indent=2)
    print(f"Figure library saved to {figure_dict_path}")

# === First Pass: Extract and Update Figures ===
def extract_figures():
    """Extract figures and update the local figure dictionary dynamically."""
    processed = 0
    for filename in os.listdir(DANCE_DIR):
        if not filename.endswith(".txt") or processed >= MAX_FILES:
            continue
        path = os.path.join(DANCE_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        code_block = extract_code_block(content)
        if not code_block:
            continue
        print(f"Extracting and matching figures from: {filename}")
        prompt = build_prompt_for_figures(code_block, local_figure_dict)
        result = run_openai_prompt(prompt)

        new_figures = result.get("figures", [])
        print(f"Extracted {len(new_figures)} figures from {filename}")
        update_figure_dict(new_figures)
        processed += 1
        if processed % INCREMENTAL_THRESHOLD == 0:
            print(f"INCREMENT: {processed // INCREMENTAL_THRESHOLD}")
            save_figure_dict()
    print(f"Figure Dictionary Generated. {len(local_figure_dict)} unique figures identified.")

def update_figure_dict(new_figures):
    """Update the local figure dictionary with new or matched figures."""
    for new_figure in new_figures:
        if new_figure['name'] not in {figure["name"] for figure in local_figure_dict}:
            local_figure_dict.append(new_figure)

# === Second Pass: Convert Dances Using Extracted Figures ===
def generate_dances():
    """Convert dances into definitions using the known figures from the local dictionary."""
    figure_library_path = os.path.join(OUTPUT_DIR, "figure_library.json")
    with open(figure_library_path, "r", encoding="utf-8") as f:
        figure_library = json.load(f)
    print("Loaded figure library:", figure_library)

    processed = 0
    for filename in os.listdir(DANCE_DIR):
        if not filename.endswith(".txt") or processed >= MAX_FILES:
            continue
        
        path = os.path.join(DANCE_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        code_block = extract_code_block(content)
        if not code_block:
            continue

        print(f"Generating dance definition for: {filename}")
        prompt = build_prompt_for_dance(code_block, figure_library)
        result = run_openai_prompt(prompt)
        dance_definition = result.get("dance_definition", {})

        output_filename = f"{os.path.splitext(filename)[0]}.json"
        output_path = os.path.join(OUTPUT_DIR, output_filename)
        with open(output_path, "w", encoding="utf-8") as out:
            json.dump(dance_definition, out, indent=2)

        print(f"Saved dance definition to {output_path}")
        processed += 1

# === Main ===
def main():
    extract_figures()
    print("Storing figure dictionary...")
    save_figure_dict()
    print("Converting dances using extracted figures...")
    generate_dances()
    
if __name__ == "__main__":
    main()
