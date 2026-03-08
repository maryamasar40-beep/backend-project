from app.celery_app import celery_app


@celery_app.task(name="tasks.analyze_screenshot")
def analyze_screenshot(scan_id: int, screenshot_hash: str | None) -> dict:
    return {
        "scan_id": scan_id,
        "status": "processed",
        "hash_present": bool(screenshot_hash),
    }


@celery_app.task(name="tasks.check_logo")
def check_logo(scan_id: int, domain: str) -> dict:
    return {
        "scan_id": scan_id,
        "domain": domain,
        "logo_match": False,
    }


@celery_app.task(name="tasks.compute_risk")
def compute_risk(scan_id: int, exact_hash_match: bool) -> dict:
    risk_score = 0.85 if exact_hash_match else 0.25
    return {"scan_id": scan_id, "risk_score": risk_score}
