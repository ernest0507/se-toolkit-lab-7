"""LMS API client for communicating with the backend."""

import httpx
from pydantic import BaseModel


class ItemRecord(BaseModel):
    """Represents a lab or task item from the backend."""

    id: int
    type: str
    title: str
    lab: str | None = None
    parent_id: int | None = None


class PassRateRecord(BaseModel):
    """Represents pass rate data for a task."""

    task: str
    avg_score: float
    attempts: int

    @property
    def pass_rate(self) -> float:
        """Return avg_score as pass_rate for compatibility."""
        return self.avg_score


class APIError(Exception):
    """Raised when the API returns an error."""

    def __init__(self, message: str, status_code: int | None = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class LMSAPIClient:
    """Client for the LMS Backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create an HTTP client with auth headers."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=30.0,
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get_items(self) -> list[ItemRecord]:
        """Fetch all items (labs and tasks) from the backend.

        Returns:
            List of ItemRecord objects.

        Raises:
            APIError: If the API returns an error.
            httpx.ConnectError: If the backend is unreachable.
        """
        client = await self._get_client()
        try:
            response = await client.get(f"{self.base_url}/items/")
            response.raise_for_status()
            data = response.json()
            return [ItemRecord.model_validate(item) for item in data]
        except httpx.ConnectError as e:
            raise APIError(
                f"connection refused ({self.base_url})", status_code=None
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. "
                f"The backend service may be down.",
                status_code=e.response.status_code,
            ) from e
        except httpx.HTTPError as e:
            raise APIError(f"request failed: {e}") from e

    async def get_pass_rates(self, lab: str) -> list[PassRateRecord]:
        """Fetch pass rates for a specific lab.

        Args:
            lab: The lab identifier (e.g., 'lab-04').

        Returns:
            List of PassRateRecord objects.

        Raises:
            APIError: If the API returns an error.
            httpx.ConnectError: If the backend is unreachable.
        """
        client = await self._get_client()
        try:
            response = await client.get(
                f"{self.base_url}/analytics/pass-rates",
                params={"lab": lab},
            )
            response.raise_for_status()
            data = response.json()
            return [PassRateRecord.model_validate(record) for record in data]
        except httpx.ConnectError as e:
            raise APIError(
                f"connection refused ({self.base_url})", status_code=None
            ) from e
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"HTTP {e.response.status_code} {e.response.reason_phrase}. "
                f"The backend service may be down.",
                status_code=e.response.status_code,
            ) from e
        except httpx.HTTPError as e:
            raise APIError(f"request failed: {e}") from e


def _get_settings():
    """Lazy import of settings to avoid circular imports."""
    from config import settings

    return settings


# Global API client instance - initialized lazily
_api_client: LMSAPIClient | None = None


def get_api_client() -> LMSAPIClient:
    """Get or create the global API client instance."""
    global _api_client
    if _api_client is None:
        settings = _get_settings()
        _api_client = LMSAPIClient(
            base_url=settings.LMS_API_BASE_URL or "http://localhost:42002",
            api_key=settings.LMS_API_KEY or "",
        )
    return _api_client
