import requests
from typing import Dict, Any, List, Optional

BASE_URL = "http://127.0.0.1:8000/api/v1"


class APIClient:
    """Frontend API client wrapper for FastAPI backend endpoints."""

    @staticmethod
    def get_dashboard_analytics() -> Optional[Dict[str, Any]]:
        try:
            res = requests.get(f"{BASE_URL}/analytics/dashboard", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    @staticmethod
    def get_patients() -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{BASE_URL}/patients/", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    @staticmethod
    def get_policies() -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{BASE_URL}/policies/", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    @staticmethod
    def submit_claim(claim_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            res = requests.post(f"{BASE_URL}/claims/", json=claim_payload, timeout=8)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    @staticmethod
    def get_claims() -> List[Dict[str, Any]]:
        try:
            res = requests.get(f"{BASE_URL}/claims/", timeout=5)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return []

    @staticmethod
    def process_ocr(doc_type: str, sample_type: str) -> Optional[Dict[str, Any]]:
        try:
            res = requests.post(
                f"{BASE_URL}/ocr/process",
                data={"doc_type": doc_type, "sample_type": sample_type},
                timeout=8
            )
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None

    @staticmethod
    def query_rag(query: str) -> Optional[Dict[str, Any]]:
        try:
            res = requests.post(f"{BASE_URL}/rag/query", json={"query": query}, timeout=8)
            if res.status_code == 200:
                return res.json()
        except Exception:
            pass
        return None
