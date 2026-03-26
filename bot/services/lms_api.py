"""Async client for interacting with LMS backend API."""

import httpx
from pydantic import BaseModel


# -------------------- Models --------------------

class Item(BaseModel):
    """Entity representing a lab or task."""

    id: int
    type: str
    title: str
    lab: str | None = None
    parent_id: int | None = None


class PassRate(BaseModel):
    """Statistics for task pass rate."""

    task: str
    avg_score: float
    attempts: int

    @property
    def pass_rate(self) -> float:
        return self.avg_score


# -------------------- Errors --------------------

class LMSAPIError(Exception):
    """Generic API exception."""

    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.message = message
        self.code = code


# -------------------- Client --------------------

class LMSClient:
    """HTTP client for LMS backend."""

    def __init__(self, base_url: str, token: str):
        self._base = base_url.rstrip("/")
        self._token = token
        self._session: httpx.AsyncClient | None = None

    async def _session_instance(self) -> httpx.AsyncClient:
        """Create or reuse HTTP session."""
        if self._session is None or self._session.is_closed:
            self._session = httpx.AsyncClient(
                timeout=30.0,
                headers={"Authorization": f"Bearer {self._token}"},
            )
        return self._session

    async def shutdown(self) -> None:
        """Close session if active."""
        if self._session and not self._session.is_closed:
            await self._session.aclose()

    # -------------------- API methods --------------------

    async def fetch_items(self) -> list[Item]:
        """Retrieve all items."""
        client = await self._session_instance()

        try:
            resp = await client.get(f"{self._base}/items/")
            resp.raise_for_status()
            payload = resp.json()
            return [Item.model_validate(x) for x in payload]

        except httpx.ConnectError as e:
            raise LMSAPIError(f"connection refused ({self._base})") from e

        except httpx.HTTPStatusError as e:
            raise LMSAPIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. Backend might be down.",
                code=e.response.status_code,
            ) from e

        except httpx.HTTPError as e:
            raise LMSAPIError(f"request failed: {e}") from e

    async def fetch_pass_rates(self, lab: str) -> list[PassRate]:
        """Retrieve pass rate analytics for a lab."""
        client = await self._session_instance()

        try:
            resp = await client.get(
                f"{self._base}/analytics/pass-rates",
                params={"lab": lab},
            )
            resp.raise_for_status()
            payload = resp.json()
            return [PassRate.model_validate(x) for x in payload]

        except httpx.ConnectError as e:
            raise LMSAPIError(f"connection refused ({self._base})") from e

        except httpx.HTTPStatusError as e:
            raise LMSAPIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. Backend might be down.",
                code=e.response.status_code,
            ) from e

        except httpx.HTTPError as e:
            raise LMSAPIError(f"request failed: {e}") from e


# -------------------- Settings loader --------------------

def _load_settings():
    """Import settings lazily."""
    from config import settings
    return settings


# -------------------- Singleton --------------------

_client: LMSClient | None = None


def get_api_client() -> LMSClient:
    """Return shared LMS client instance."""
    global _client

    if _client is None:
        cfg = _load_settings()
        _client = LMSClient(
            base_url=cfg.LMS_API_BASE_URL or "http://localhost:42002",
            token=cfg.LMS_API_KEY or "",
        )

    return _client
