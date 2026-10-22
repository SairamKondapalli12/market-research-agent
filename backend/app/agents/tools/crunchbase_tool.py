"""Optional Crunchbase lookup tool (requires CRUNCHBASE_API_KEY)."""

from typing import Any, Dict, List, Optional

import httpx

from app.config.logging_config import get_logger
from app.config.settings import settings

logger = get_logger(__name__)


class CrunchbaseTool:
    """Fetches funding data from Crunchbase (paid tier required)."""

    BASE_URL = "https://api.crunchbase.com/api/v4"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or getattr(settings, "CRUNCHBASE_API_KEY", None)

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def lookup(self, company_name: str) -> Dict[str, Any]:
        if not self.available:
            return {"success": False, "error": "Crunchbase API key not configured"}

        try:
            with httpx.Client(timeout=15) as client:
                resp = client.post(
                    f"{self.BASE_URL}/searches/organizations",
                    params={"user_key": self.api_key},
                    json={
                        "field_ids": [
                            "identifier",
                            "short_description",
                            "funding_total",
                            "num_funding_rounds",
                            "last_funding_type",
                            "last_funding_at",
                            "investor_identifiers",
                        ],
                        "query": [
                            {
                                "type": "predicate",
                                "field_id": "identifier",
                                "operator_id": "contains",
                                "values": [company_name.lower()],
                            }
                        ],
                        "limit": 1,
                    },
                )
                resp.raise_for_status()
                data = resp.json()
                entities = data.get("entities", [])
                if not entities:
                    return {"success": False, "error": "No match found"}
                return {"success": True, "entity": entities[0]}
        except Exception as exc:
            logger.warning(f"Crunchbase lookup failed: {exc}")
            return {"success": False, "error": str(exc)}