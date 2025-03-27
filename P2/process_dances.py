import os
import re
import json
from openai import OpenAI
from dotenv import load_dotenv

# === Config ===
MAX_FILES = 10 
DANCE_DIR = "dances"
OUTPUT_DIR = "output"
MODEL = "gpt-4o"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# === OpenAI client ===
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# === Few-shot example for The Adieu ===
THE_ADIEU_EXAMPLE = """Dance Name: The Adieu
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
</code>"""

EXPECTED_JSON_OUTPUT = {
  "figure_library": [
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

def extract_code_blocks(text):
    """Extracts all content between <code>...</code> tags."""
    return re.findall(r"<code>(.*?)</code>", text, re.DOTALL)

def build_prompt(code_block):
    return [
        {
            "role": "system",
            "content": (
                "You are a helpful assistant that converts English Country Dance instructions into structured JSON.\n"
                "Given a dance, respond ONLY with a JSON object that contains two keys:\n"
                "  1. 'figure_library': a list of reusable figures with name, roles, action, start_position, end_position, and duration.\n"
                "  2. 'dance_definition': including title, formation, music_structure, and a phrases section (A, B, C, etc.) listing figure names.\n"
                "Use the following example as a format guide and match its structure."
            )
        },
        {
            "role": "user",
            "content": THE_ADIEU_EXAMPLE
        },
        {
            "role": "assistant",
            "content": json.dumps(EXPECTED_JSON_OUTPUT, indent=2)
        },
        {
            "role": "user",
            "content": f"Convert this dance:\n<code>{code_block}</code>"
        }
    ]

def main():
    processed = 0

    for filename in os.listdir(DANCE_DIR):
        if not filename.endswith(".txt") or processed >= MAX_FILES:
            continue

        path = os.path.join(DANCE_DIR, filename)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        code_blocks = extract_code_blocks(content)
        if not code_blocks:
            continue

        print(f"Processing: {filename}")
        for i, code in enumerate(code_blocks):
            prompt = build_prompt(code)
            response = client.chat.completions.create(
                model=MODEL,
                messages=prompt,
                response_format="json"
            )
            result = response.choices[0].message.content

            output_filename = f"{os.path.splitext(filename)[0]}_block{i+1}.json"
            output_path = os.path.join(OUTPUT_DIR, output_filename)
            with open(output_path, "w", encoding="utf-8") as out_file:
                out_file.write(result)
            print(f"✓ Saved to {output_path}")

        processed += 1

if __name__ == "__main__":
    main()
