import csv
import json
import subprocess
import os
import re
from datetime import datetime

TEST_CASES = "evaluation/test_cases.csv"
# MODEL_LABEL = "llama70b"
# MODEL_LABEL = "llama8b"
MODEL_LABEL = "DEFAULT"
MODEL_TIMEOUT = 600
OUTPUT_FILE = (
    f"evaluation/gesture_eval_results_{MODEL_LABEL}.csv"
)

PYTHON_EXE = "py"
PYTHON_VERSION = "-3.10"

LANGCHAIN_SCRIPT = "langchain_query.py"
INDEX_DIR = "knowledge_base/artikel/faiss_index"
MODE = "quiz"

RUNS_PER_TEST = 3

ALLOWED_GESTURES = {
    "acknowledging_pose", "thinking_pose", "head_nod_yes", "thoughtful_head_nod",
    "head_shake_no", "talk_pose", "talk_pose2", "talk_pose3", "arm_gesture",
    "pointing_pose", "pointing_forward", "surprised_pose", "hello_pose", "bye_pose"
}

STRONG_GESTURES = {
    "surprised_pose",
    "head_shake_no",
    "pointing_forward",
    "pointing_pose"
}


def clear_history():
    with open("history.txt", "w", encoding="utf-8") as f:
        f.write("")


def run_model(user_input):
    cmd = [
        PYTHON_EXE,
        PYTHON_VERSION,
        LANGCHAIN_SCRIPT,
        user_input,
        INDEX_DIR,
        MODE
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=MODEL_TIMEOUT
        )
    except subprocess.TimeoutExpired:
        return {
            "error": (
                f"Model timeout after {MODEL_TIMEOUT} seconds."
            ),
            "response": "",
            "gestures": []
        }

    if result.returncode != 0:
        return {
            "error": result.stderr.strip(),
            "response": "",
            "gestures": []
        }

    stdout = result.stdout.strip()

    try:
        data = json.loads(stdout)
        return {
            "error": "",
            "response": data.get("response", ""),
            "gestures": data.get("gestures", [])
        }
    except Exception as e:
        return {
            "error": (
                f"JSON parse error: {e}. "
                f"Raw stdout: {stdout}"
            ),
            "response": "",
            "gestures": []
        }

def split_into_segments(text):
    clean_text = re.sub(r"\([^)]*\)", "", text)
    clean_text = re.sub(r"\[[^\]]*\]", "", clean_text)
    clean_text = re.sub(r"[()]", "", clean_text)
    clean_text = re.sub(r"\s+", " ", clean_text).strip()

    parts = re.findall(
        r"[^.!?]+[.!?]+|[^.!?]+$",
        clean_text
    )

    return [
        part.strip()
        for part in parts
        if len(part.strip()) > 1
        and part.strip() not in {"(", ")"}
    ]

def evaluate_result(gestures, expected_gestures, strong_allowed):
    expected_set = set(g.strip() for g in expected_gestures.split("|") if g.strip())
    strong_allowed_set = set(g.strip() for g in strong_allowed.split("|") if g.strip())

    valid_gestures = [g for g in gestures if g in ALLOWED_GESTURES]
    invalid_gestures = [g for g in gestures if g not in ALLOWED_GESTURES]

    matching_gestures = [g for g in gestures if g in expected_set]
    contains_expected_gesture = any(g in expected_set for g in gestures)
    first_gesture_match = gestures[0] in expected_set if gestures else False

    used_strong = [g for g in gestures if g in STRONG_GESTURES]
    wrongly_used_strong = [
        g for g in used_strong
        if g not in strong_allowed_set and g not in expected_set
    ]

    valid_rate = len(valid_gestures) / len(gestures) if gestures else 0
    match_rate = len(matching_gestures) / len(gestures) if gestures else 0

    if invalid_gestures:
        score = 0
        comment = "Invalid gesture generated."

    elif match_rate < 0.3:
        score = 0
        comment = "Gestures do not match expected category well."

    elif wrongly_used_strong:
        score = 1
        comment = (
            "Strong gesture may be overused or "
            "semantically questionable."
        )

    elif match_rate < 0.6:
        score = 1
        comment = "Gestures partially match expected category."

    else:
        score = 2
        comment = "Gestures mostly match expected category."

    return {
        "valid_count": len(valid_gestures),
        "invalid_gestures": "|".join(invalid_gestures),
        "matching_gestures": "|".join(matching_gestures),
        "used_strong_gestures": "|".join(used_strong),
        "wrongly_used_strong": "|".join(wrongly_used_strong),
        "valid_rate": round(valid_rate, 2),
        "match_rate": round(match_rate, 2),
        "contains_expected_gesture": contains_expected_gesture,
        "first_gesture_match": first_gesture_match,
        "auto_score": score,
        "auto_comment": comment
    }


def main():
    os.makedirs("evaluation", exist_ok=True)

    rows = []

    with open(TEST_CASES, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        test_cases = list(reader)

    for run_id in range(1, RUNS_PER_TEST + 1):
        print(f"Starting run {run_id}/{RUNS_PER_TEST}")

        for case in test_cases:
            clear_history()

            test_id = case["id"]
            category = case["category"]
            user_input = case["input"]
            expected_gestures = case["expected_gestures"]
            strong_allowed = case.get("strong_allowed", "")

            print(f"Test {test_id}, run {run_id}: {user_input}")

            result = run_model(user_input)
            response = result["response"]
            gestures = result["gestures"]
            segments = split_into_segments(response)
            used_gestures = [
                gestures[i] if i < len(gestures) else "talk_pose"
                for i in range(len(segments))
            ]
            error = result["error"]

            eval_data = evaluate_result(
                used_gestures,
                expected_gestures,
                strong_allowed
            )

            row = {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "model": MODEL_LABEL,
                "run_id": run_id,
                "test_id": test_id,
                "category": category,
                "input": user_input,
                "expected_gestures": expected_gestures,
                "strong_allowed": strong_allowed,
                "response": response,
                "all_gestures": "|".join(gestures),
                "segment_count": len(segments),
                "used_gestures": "|".join(used_gestures),
                "valid_count": eval_data["valid_count"],
                "invalid_gestures": eval_data["invalid_gestures"],
                "matching_gestures": eval_data["matching_gestures"],
                "used_strong_gestures":
                    eval_data["used_strong_gestures"],
                "wrongly_used_strong":
                    eval_data["wrongly_used_strong"],
                "valid_rate": eval_data["valid_rate"],
                "match_rate": eval_data["match_rate"],
                "contains_expected_gesture":
                    eval_data["contains_expected_gesture"],
                "first_gesture_match":
                    eval_data["first_gesture_match"],
                "auto_score": eval_data["auto_score"],
                "auto_comment": eval_data["auto_comment"],
                "error": error
            }

            rows.append(row)

    fieldnames = list(rows[0].keys())

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Done. Results written to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()