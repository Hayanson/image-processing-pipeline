# app/retrain_issue.py
from datetime import datetime
import logging
from app.config import LOW_CONFIDENCE_THRESHOLD
from issue import create_github_issue 

logger = logging.getLogger(__name__)

_state = {
    "low_confidence_count": 0,
    "samples": [],
    "issue_created": False,
}

LOW_CONFIDENCE_LIMIT = 5

def update_issue_state(features: dict, predicted_style: str, score: float, threshold: float):
    # drift 의심 시 GitHub Issue 생성 로직
    if score < threshold:
        _state["low_confidence_count"] += 1
        _state["samples"].append({
            "features": features, # 밝기, 대조도 등 이미지 특성
            "style": predicted_style,
            "score": round(float(score), 4),
            "time": datetime.now().isoformat(timespec="seconds")
        })
        
        # 임곗값을 넘으면 issue 생성
        if _state["low_confidence_count"] >= LOW_CONFIDENCE_LIMIT and not _state["issue_created"]:
            create_drift_issue()
            _state["issue_created"] = True

def create_drift_issue():
    samples = _state["samples"][-5:]
    title = "[MLOps] Drift suspected (Low confidence in Style Model)"
    
    body = f"""
## Drift Detection Report
Low-confidence predictions accumulated.

- count: {_state["low_confidence_count"]}
- threshold: {LOW_CONFIDENCE_LIMIT}

## Recent Samples
"""
    for s in samples:
        body += f"- Score: {s['score']} | Predicted: {s['style']} | Features: {s['features']}\n"
        
    body += """
## Action
- Please review image data distributions
- Decide whether retraining is needed
"""
    create_github_issue(title, body, logger)