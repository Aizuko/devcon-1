import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from db import get_progress, update_progress

app = FastAPI(title="SecurityPrep API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load questions at startup
with open("questions.json") as f:
    QUESTIONS: list[dict] = json.load(f)

MODULE_NAMES = {
    1: "The Security Industry",
    2: "Legal Authority",
    3: "Criminal & Civil Law",
    4: "Report Writing",
    5: "Health & Safety",
    6: "Emergency Response",
    7: "Communication & Conflict",
}


# ── Models ──

class LoginReq(BaseModel):
    name: str

class AnswerReq(BaseModel):
    user_name: str
    question_id: str
    selected: int
    feedback: str | None = None  # "happy", "sad", or null (wrong answer)


# ── Endpoints ──

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/login")
def login(req: LoginReq):
    return {"user_name": req.name}


@app.get("/api/modules")
def list_modules():
    counts = {}
    for q in QUESTIONS:
        counts[q["module"]] = counts.get(q["module"], 0) + 1
    return [
        {"id": mid, "name": MODULE_NAMES.get(mid, f"Module {mid}"), "question_count": cnt}
        for mid, cnt in sorted(counts.items())
    ]


@app.get("/api/modules/{module_id}/status")
def module_status(module_id: int, user_name: str):
    mod_qs = [q for q in QUESTIONS if q["module"] == module_id]
    if not mod_qs:
        return {"total": 0, "completed": 0, "percent": 0}
    progress = get_progress(user_name, module_id)
    completed = sum(1 for q in mod_qs if progress.get(q["id"], {}).get("completed", False))
    return {"total": len(mod_qs), "completed": completed, "percent": round(completed / len(mod_qs) * 100)}


@app.get("/api/modules/{module_id}/next-question")
def next_question(module_id: int, user_name: str):
    mod_qs = [q for q in QUESTIONS if q["module"] == module_id]
    if not mod_qs:
        return {"module_complete": True}
    progress = get_progress(user_name, module_id)

    # Find first uncompleted question
    for q in mod_qs:
        p = progress.get(q["id"])
        if p and p["completed"]:
            continue
        level = p["level"] if p else 1
        level_data = q["levels"][str(level)]
        return {
            "module_complete": False,
            "question_id": q["id"],
            "level": level,
            "question": level_data["question"],
            "options": level_data["options"],
            "correct": q["correct"],
        }

    return {"module_complete": True}


@app.post("/api/answer")
def answer(req: AnswerReq):
    # Find the question
    q = next((q for q in QUESTIONS if q["id"] == req.question_id), None)
    if not q:
        return {"error": "question not found"}

    module_id = q["module"]
    progress = get_progress(req.user_name, module_id)
    p = progress.get(req.question_id)
    current_level = p["level"] if p else 1
    is_correct = req.selected == q["correct"]

    if is_correct:
        if req.feedback == "happy":
            new_level = min(current_level + 1, 3)
        else:  # sad
            new_level = current_level
        completed = is_correct and new_level == 3 and current_level == 3
    else:
        new_level = max(current_level - 1, 1)
        completed = False

    update_progress(req.user_name, req.question_id, new_level, completed)
    return {"correct": is_correct, "new_level": new_level, "completed": completed}
