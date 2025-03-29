import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# === Config ===
MAX_FILES = 3
DANCE_DIR = "dances"
OUTPUT_DIR = "output"
MODEL = "gpt-4o-mini"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === OpenAI Client ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# === Local Figure Dictionary ===
local_figure_dict = []

# === Few Shot Example ===
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
    {
      "name": "Face Down and Take Right Hands",
      "roles": "All",
      "start_position": "Facing across the set",
      "action": "Turn to face down set; take right hands with partner",
      "end_position": "Ready to lead down",
      "duration": 2
    },
    {
      "name": "Lead Down and Up with Turn Under",
      "roles": "All",
      "start_position": "Facing down, right hands joined",
      "action": "Lead down the set; women turn under joined hands; lead back up",
      "end_position": "Back at starting place",
      "duration": 8
    },
    {
      "name": "Cast and Form Center Line",
      "roles": "1st and 3rd couples",
      "start_position": "Top and bottom of set",
      "action": "Cast one place; men end back to back with partner on center line",
      "end_position": "1st and 3rd couples centered, men below women",
      "duration": 4
    },
    {
      "name": "Take Hands in Groups",
      "roles": "All",
      "start_position": "Varies",
      "action": "Take hands 3 at top & bottom; hands 4 in the middle",
      "end_position": "Ready to set",
      "duration": 2
    },
    {
      "name": "Set and Circle Left",
      "roles": "All",
      "start_position": "In groups from previous figure",
      "action": "Set right and left; circle left; break to original partner",
      "end_position": "Facing partner in progressed place",
      "duration": 8
    },
    {
      "name": "Overhead Allemande Right",
      "roles": "Partners",
      "start_position": "Facing partner",
      "action": "Take right hands; woman moves forward and back while man gypsies clockwise, she passes under",
      "end_position": "Partners on original sides",
      "duration": 8
    },
    {
      "name": "Final Cast and Left-Hand Allemande",
      "roles": "1st and 3rd couples cast; others allemande",
      "start_position": "After previous allemande",
      "action": "1st and 3rd couples cast out; others do left-hand overhead allemande moving up",
      "end_position": "All progressed, back to longways formation",
      "duration": 8
    }
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

# === Functions ===
def extract_code_block(text):
  """Extracts all content between <code>...</code> tags."""
  match = re.search(r"<code>(.*?)</code>", text, re.DOTALL)
  if match:
    return match.group(1)
  return None

def build_prompt_for_figures(code_block, figure_dict):
  """Create a few-shot prompt to extract figures or match them with the existing dictionary"""
  figure_dict_content = json.dumps(figure_dict, indent=2)

  return [
    {
      "role": "system",
      "content": (
        "You are a helpful assistant that converts English Country Dance instructions into structured JSON with key \"figures\" and a value list of figures.\n"
        "Each figure should include:\n"
        "- name\n"
        "- roles\n"
        "- action\n"
        "- start_position\n"
        "- end_position\n"
        "- duration\n\n"
        "You are also given an updated dictionary of known figures in JSON format.\n"
        "When extracting figures from the new dance instructions, use the dictionary to:\n"
        "1. Match similar figures and reuse their names if the new figure is similar.\n"
        "2. Create a new figure if no sufficiently similar match is found.\n\n"
        "You should always prioritize reusing similar figures instead of defining new ones."
        f"Here is an example with 'The Adieu':\n{THE_ADIEU_EXAMPLE}\n\n\"figures\": {json.dumps(EXPECTED_JSON_OUTPUT['figures'], indent=2)}\n\n"
        f"Current figure dictionary:\n{figure_dict_content}"
      )
    },
    {
      "role": "user",
      "content": f"Extract and match figures from this dance:\n<code>{code_block}</code>"
    }
  ]

def build_prompt_for_dance(code_block, figure_dict):
  """Create a few-shot prompt to map a dance to known figures."""
  figure_dict_content = json.dumps(figure_dict, indent=2)

  return [
    {
      "role": "system",
      "content": (
        "You are a helpful assistant that converts English Country Dance instructions into structured JSON.\n"
        "Given a dance and a dictionary of known figures, respond ONLY with a JSON object that has key \"dance_definition\" and value list:\n"
        "title, formation, music_structure, and a phrases section (A, B, C, etc.) listing figure names.\n"
        "Use only the provided figure names to map the dance.\n\n"
        f"Here is an example with 'The Adieu':\n{THE_ADIEU_EXAMPLE}\n"
        f"For this example, the available dictionary of known figures was:\n{json.dumps(EXPECTED_JSON_OUTPUT['figures'], indent=2)}\n\n"
        f"The output was \"dance_definition\": {json.dumps(EXPECTED_JSON_OUTPUT['dance_definition'], indent=2)}\n\n"
        f"The current known figures:\n{figure_dict_content}"
      )
    },
    {
      "role": "user",
      "content": f"Convert this dance into a definition using only known figures:\n<code>{code_block}</code>"
    }
  ]

def run_openai_prompt(prompt):
  """Send a prompt to OpenAI and return the JSON response."""
  response = client.chat.completions.create(
    model=MODEL,
    messages=prompt,
    response_format={"type": "json_object"}
  )
  return json.loads(response.choices[0].message.content)

# === First Pass: Extract and Update Figures ===
def extract_figures():
  """Extract figures and dynamically update the local figure dictionary"""
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
  print(f"Figure Dictionary Generated. {len(local_figure_dict)} unique figures identified.")

def update_figure_dict(new_figures):
  """Update the local figure dictionary with new or matched figures."""
  for new_figure in new_figures:
    existing_names = [figure["name"] for figure in local_figure_dict]
    if new_figure['name'] not in existing_names:
      local_figure_dict.append(new_figure)

# === Second Pass: Convert Dances using Extracted Figures ===
def generate_dances():
  """Convert dances using known figures in the local dictionary"""
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

    print(f"Generating dance definitions for: {filename}.")
    prompt = build_prompt_for_dance(code_block, local_figure_dict)
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
  figure_dict_path = os.path.join(OUTPUT_DIR, "figure_library.json")
  with open(figure_dict_path, "w", encoding="utf-8") as f:
    json.dump(local_figure_dict, f, indent=2)
  print(f"Figure library saved to {figure_dict_path}")
  print("Convert dances using extracted figures...")
  generate_dances()
    
if __name__ == "__main__":
    main()
