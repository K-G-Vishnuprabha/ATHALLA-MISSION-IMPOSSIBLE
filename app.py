import random
import time
import uuid
from flask import Flask, jsonify, render_template, request
from data import OBJECTS, WRONG_REACTIONS, REPEATS, ACCEPT, RANKS

app = Flask(__name__)
GAMES = {}

SLOT_META = {
    "table-left": {"x": 25, "y": 51, "surface": "മേശപ്പുറത്ത്"},
    "table-mid-left": {"x": 34, "y": 47, "surface": "മേശപ്പുറത്ത്"},
    "table-center": {"x": 43, "y": 50, "surface": "മേശപ്പുറത്ത്"},
    "table-mid-right": {"x": 51, "y": 47, "surface": "മേശപ്പുറത്ത്"},
    "table-right": {"x": 59, "y": 52, "surface": "മേശപ്പുറത്ത്"},
    "shelf-left-top": {"x": 65, "y": 20, "surface": "ഷെൽഫിന്റെ മുകളിൽ"},
    "shelf-center-top": {"x": 75, "y": 18, "surface": "ഷെൽഫിന്റെ മുകളിൽ"},
    "shelf-right-top": {"x": 85, "y": 21, "surface": "ഷെൽഫിന്റെ മുകളിൽ"},
    "shelf-left": {"x": 65, "y": 31, "surface": "ഷെൽഫിൽ"},
    "shelf-center": {"x": 75, "y": 29, "surface": "ഷെൽഫിൽ"},
    "shelf-right": {"x": 85, "y": 32, "surface": "ഷെൽഫിൽ"},
    "chair-seat-left": {"x": 12, "y": 55, "surface": "കസേരയിൽ"},
    "chair-seat": {"x": 18, "y": 62, "surface": "കസേരയിൽ"},
    "chair-back": {"x": 13, "y": 39, "surface": "കസേരയുടെ മുകളിൽ"},
    "window-sill-left": {"x": 29, "y": 26, "surface": "ജനൽപ്പടിയിൽ"},
    "window-sill-right": {"x": 38, "y": 26, "surface": "ജനൽപ്പടിയിൽ"},
    "floor-far-left": {"x": 20, "y": 78, "surface": "തറയിൽ"},
    "floor-left": {"x": 32, "y": 83, "surface": "തറയിൽ"},
    "floor-mid-left": {"x": 44, "y": 79, "surface": "തറയിൽ"},
    "floor-mid-right": {"x": 56, "y": 83, "surface": "തറയിൽ"},
    "floor-right": {"x": 70, "y": 78, "surface": "തറയിൽ"},
    "floor-far-right": {"x": 85, "y": 82, "surface": "തറയിൽ"},
}


def public_object(item, slot):
    meta = SLOT_META[slot]
    return {"id": item["id"], "name": item["name"], "category": item["category"], "color": item["color"], "use": item["use"], "illustration": item["illustration"], "size": item["size"], "x": meta["x"], "y": meta["y"], "surface": meta["surface"]}


def choose_scene(game):
    previous_ids = set(game["recent_scenes"][-1]) if game["recent_scenes"] else set()
    recent_ids = {item_id for scene in game["recent_scenes"][-3:] for item_id in scene}
    picked = []
    for _ in range(80):
        candidates = sorted(OBJECTS, key=lambda item: (item["id"] in previous_ids, item["id"] in recent_ids, random.random()))
        attempt = []
        used_slots = set()
        for item in candidates:
            available = [slot for slot in item["slots"] if slot not in used_slots]
            if not available:
                available = [slot for slot in SLOT_META if slot not in used_slots]
            if available:
                slot = random.choice(available)
                attempt.append(public_object(item, slot))
                used_slots.add(slot)
            if len(attempt) == 22:
                break
        if len(attempt) == 22:
            picked = attempt
            break
    if len(picked) < 22:
        raise RuntimeError("Not enough distinct placement slots")
    previous_target = game.get("target_id")
    target_candidates = [item for item in picked if item["id"] != previous_target]
    target = random.choice(target_candidates)
    game["objects"] = picked
    game["target_id"] = target["id"]
    game["rejected"] = []
    game["wrong_attempts"] = 0
    game["frustration"] = 0
    game["hint_index"] = 0
    game["interaction_id"] = str(uuid.uuid4())
    game["started_at"] = None
    game["resolved"] = False
    game["takeover"] = False
    game["recent_scenes"].append([item["id"] for item in picked])
    game["recent_scenes"] = game["recent_scenes"][-5:]
    game["recent_targets"].append(target["id"])
    game["recent_targets"] = game["recent_targets"][-5:]


def scene_payload(game, include_target=False):
    payload = {"interactionId": game["interaction_id"], "objects": game["objects"], "wrongAttempts": game["wrong_attempts"], "frustration": game["frustration"], "score": game["score"], "interactionNumber": game["interaction_number"], "totalInteractions": 6, "resolved": game["resolved"]}
    if include_target:
        payload["secretTargetId"] = game["target_id"]
    return payload


def make_hint(game):
    target = next(item for item in game["objects"] if item["id"] == game["target_id"])
    previous = game.get("last_hint")
    nearby = sorted((item for item in game["objects"] if item["id"] != target["id"]), key=lambda item: abs(item["x"] - target["x"]) + abs(item["y"] - target["y"]))
    options = ["ആ സാധനം ഒന്ന് എടുത്തോണ്ട് വാ.", f"{target['surface']} ഇരിക്കുന്നത് ഒന്ന് എടുത്തേ.", f"{target['color']} നിറത്തിലുള്ളത് ഒന്ന് നോക്കിയേ.", f"{target['use']}."]
    if nearby:
        options.append(f"{nearby[0]['name']}യുടെ അടുത്തിരിക്കുന്ന സാധനം നോക്കിയേ.")
    options = [hint for hint in options if hint != previous] or [options[0]]
    hint = options[min(game["hint_index"], len(options) - 1)]
    game["hint_index"] += 1
    game["last_hint"] = hint
    return hint


def get_game():
    session_id = request.headers.get("X-Athalla-Session")
    if not session_id or session_id not in GAMES:
        return None, None
    return session_id, GAMES[session_id]


def result_payload(game):
    score = max(0, game["score"])
    rank = next(label for threshold, label in RANKS if score >= threshold)
    return {"score": score, "interactionsCompleted": game["solved"], "correctObjects": game["correct_objects"], "takeovers": game["takeovers"], "wrongAttempts": game["total_wrong"], "rank": rank, "complete": game["interaction_number"] >= 6 and game["resolved"]}


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/start")
def start():
    session_id = str(uuid.uuid4())
    game = {"score": 0, "solved": 0, "takeovers": 0, "total_wrong": 0, "correct_objects": [], "interaction_number": 1, "recent_scenes": [], "recent_targets": [], "last_hint": None}
    choose_scene(game)
    GAMES[session_id] = game
    return jsonify({"sessionId": session_id, "scene": scene_payload(game), "hint": make_hint(game)})


@app.post("/api/select")
def select():
    session_id, game = get_game()
    body = request.get_json(silent=True) or {}
    if not game or body.get("interactionId") != game["interaction_id"]:
        return jsonify({"error": "കാലഹരണപ്പെട്ട കളി. വീണ്ടും തുടങ്ങൂ."}), 409
    object_id = body.get("objectId")
    visible_ids = {item["id"] for item in game["objects"]}
    if object_id not in visible_ids:
        return jsonify({"error": "ഈ സാധനം ഈ മുറിയിൽ ഇല്ല."}), 400
    if game["resolved"]:
        return jsonify({"error": "ഈ തിരഞ്ഞെടുപ്പ് ഇപ്പോൾ സാധുവല്ല."}), 409
    if object_id in game["rejected"]:
        return jsonify({"result": "repeat", "dialogue": "അത് അല്ലെന്ന് പറഞ്ഞില്ലേ!", "scene": scene_payload(game), "hint": make_hint(game)})
    if game["started_at"] is None:
        game["started_at"] = time.time()
    if object_id == game["target_id"]:
        elapsed = time.time() - game["started_at"]
        bonus = max(0, round(30 * max(0, 1 - elapsed / 30)))
        game["score"] += 100 + bonus
        game["solved"] += 1
        game["correct_objects"].append(object_id)
        game["resolved"] = True
        return jsonify({"result":"correct", "dialogue": ACCEPT, "bonus": bonus, "scene": scene_payload(game, True), "pickupObjectId": object_id})
    game["rejected"].append(object_id)
    game["wrong_attempts"] += 1
    game["total_wrong"] += 1
    game["frustration"] = min(100, game["wrong_attempts"] * 33 + (1 if game["wrong_attempts"] == 3 else 0))
    game["score"] = max(0, game["score"] - 10)
    if game["wrong_attempts"] >= 3:
        game["resolved"] = True
        game["takeover"] = True
        game["takeovers"] += 1
        return jsonify({"result":"takeover", "dialogue":"നിന്നെ കൊണ്ട് ഒരു ഉപയോഗവും ഇല്ല!", "pointDialogue":"ഇതല്ലേ ഇവിടെ ഇരിക്കുന്നേ!", "pickupDialogue":"ഇത് തന്നെയല്ലേ ഞാൻ പറഞ്ഞത്!", "scene": scene_payload(game, True), "pickupObjectId": game["target_id"], "rejected": game["rejected"]})
    return jsonify({"result":"wrong", "dialogue": WRONG_REACTIONS[min(game["wrong_attempts"] - 1, len(WRONG_REACTIONS) - 1)], "hint": make_hint(game), "scene": scene_payload(game), "rejected": game["rejected"]})


@app.post("/api/hint")
def hint():
    _, game = get_game()
    if not game or game["resolved"]:
        return jsonify({"error": "ഇപ്പോൾ സൂചന നൽകാൻ കഴിയില്ല."}), 409
    return jsonify({"hint": make_hint(game)})


@app.post("/api/next")
def next_scene():
    _, game = get_game()
    if not game or not game["resolved"]:
        return jsonify({"error": "ഇപ്പോഴത്തെ കാര്യം ആദ്യം തീർക്കൂ."}), 409
    if game["interaction_number"] >= 6:
        return jsonify({"final": True, "result": result_payload(game)})
    game["interaction_number"] += 1
    choose_scene(game)
    return jsonify({"final": False, "scene": scene_payload(game), "hint": make_hint(game)})


@app.get("/api/result")
def result():
    _, game = get_game()
    if not game:
        return jsonify({"error": "കളി കണ്ടെത്തിയില്ല."}), 404
    return jsonify(result_payload(game))


if __name__ == "__main__":
    app.run(debug=True, port=5004)
