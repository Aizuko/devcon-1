"""
Seed script: reads questions.toml, calls Bedrock (Claude 3 Haiku) to generate
French (L1) and simplified English (L2) variants, outputs questions.json.

Usage:
    python seed_questions.py                  # uses default region us-east-1
    AWS_REGION=us-west-2 python seed_questions.py
"""

import json, os, time, tomli, boto3

REGION = os.environ.get("AWS_REGION", "us-east-1")
MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")
TOML_PATH = "questions.toml"
OUTPUT_PATH = "questions.json"

bedrock = boto3.client("bedrock-runtime", region_name=REGION)


def call_bedrock(prompt: str) -> str:
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": prompt}],
    })
    resp = bedrock.invoke_model(modelId=MODEL_ID, body=body, contentType="application/json")
    result = json.loads(resp["body"].read())
    return result["content"][0]["text"]


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

    prompt = f"""{instruction}

Question: {question}
Options: {json.dumps(options)}"""

    for attempt in range(3):
        try:
            raw = call_bedrock(prompt)
            # Strip markdown fences if present
            text = raw.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            return json.loads(text)
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
        time.sleep(0.5)  # rate limit courtesy

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
