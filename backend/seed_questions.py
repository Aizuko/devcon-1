"""
Seed script: reads questions.toml, calls Bedrock (via OpenAI-compatible endpoint)
to generate French (L1) and simplified English (L2) variants, outputs questions.json.

Usage:
    export OPENAI_API_KEY="bedrock-api-key-..."
    export OPENAI_BASE_URL="https://bedrock-mantle.us-west-2.api.aws/v1"
    python seed_questions.py
"""

import json, os, time, tomli
from openai import OpenAI

TOML_PATH = "questions.toml"
OUTPUT_PATH = "questions.json"
MODEL = os.environ.get("BEDROCK_MODEL", "anthropic.claude-3-haiku-20240307-v1:0")

client = OpenAI()


def call_llm(prompt: str) -> str:
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
    )
    return resp.choices[0].message.content


def generate_variant(question: str, options: list[str], mode: str) -> dict:
    if mode == "french":
        instruction = (
            "Translate the following multiple-choice question and its options into French. "
            "Return ONLY a JSON object with keys \"question\" (string) and \"options\" (array of strings). No extra text."
        )
    else:
        instruction = (
            "Rewrite the following multiple-choice question and its options in very simple English "
            "suitable for a grade 3 reading level. Keep the meaning identical. "
            "Return ONLY a JSON object with keys \"question\" (string) and \"options\" (array of strings). No extra text."
        )

    prompt = f"{instruction}\n\nQuestion: {question}\nOptions: {json.dumps(options)}"

    for attempt in range(3):
        try:
            raw = call_llm(prompt).strip()
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(raw)
        except Exception as e:
            print(f"  Attempt {attempt+1} failed ({e}), retrying...")
            time.sleep(2)
    raise RuntimeError(f"Failed after 3 attempts for: {question[:50]}")


def main():
    with open(TOML_PATH, "rb") as f:
        data = tomli.load(f)

    output = []
    for q in data["questions"]:
        print(f"Processing {q['id']}...")

        french = generate_variant(q["question"], q["options"], "french")
        print(f"  ✓ French")
        time.sleep(0.5)

        simple = generate_variant(q["question"], q["options"], "simple")
        print(f"  ✓ Simple English")
        time.sleep(0.5)

        output.append({
            "id": q["id"],
            "module": q["module"],
            "correct": q["correct"],
            "levels": {
                "1": {"question": french["question"], "options": french["options"]},
                "2": {"question": simple["question"], "options": simple["options"]},
                "3": {"question": q["question"], "options": q["options"]},
            },
        })

    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Generated {OUTPUT_PATH} with {len(output)} questions")


if __name__ == "__main__":
    main()
