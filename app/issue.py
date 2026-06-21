import os
import requests

def create_github_issue(title: str, body: str, logger) -> None:
    repo = os.getenv("GH_REPO")
    token = os.getenv("GH_TOKEN")
    
    if not repo or not token:
        logger.warning("GH_REPO나 GH_TOKEN이 설정되지 않아 이슈 생성을 건너뜁니다.")
        return
        
    url = f"https://api.github.com/repos/{repo}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    payload = {"title": title, "body": body}
    
    r = requests.post(url, headers=headers, json=payload, timeout=10)
    if r.status_code >= 300:
        logger.warning(f"이슈 생성 실패: {r.status_code} {r.text[:200]}")