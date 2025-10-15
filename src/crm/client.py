"""CRM API client for lead management."""

import logging
from typing import Optional

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


class LeadResponse:
    """Response from CRM lead creation."""

    def __init__(self, success: bool, lead_id: Optional[str] = None, error: Optional[str] = None):
        """Initialize lead response.

        Args:
            success: Whether lead creation succeeded
            lead_id: Lead ID from CRM (if successful)
            error: Error message (if failed)
        """
        self.success = success
        self.lead_id = lead_id
        self.error = error


class CRMClient:
    """Client for CRM API interactions."""

    def __init__(self, api_url: str = None, api_key: str = None):
        """Initialize CRM client.

        Args:
            api_url: CRM API base URL
            api_key: CRM API key
        """
        self.api_url = api_url or settings.crm_api_url
        self.api_key = api_key or settings.crm_api_key
        self.max_retries = 3

    async def create_lead(self, name: str, email: str, phone: str) -> LeadResponse:
        """Create a lead in the CRM system.

        Args:
            name: Customer name
            email: Customer email
            phone: Customer phone

        Returns:
            LeadResponse with result
        """
        payload = {
            "name": name,
            "email": email,
            "phone": phone,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        url = f"{self.api_url}/ctream-crm/api/v1/leads"

        # Retry logic with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.post(url, json=payload, headers=headers)

                    if response.status_code == 201:
                        # Success
                        data = response.json()
                        lead_id = data.get("id") or data.get("lead_id")
                        logger.info(f"Lead created successfully: {lead_id}")
                        return LeadResponse(success=True, lead_id=lead_id)

                    elif response.status_code == 400:
                        # Bad request - don't retry
                        error = response.json().get("error", "Invalid request")
                        logger.error(f"Lead creation failed (400): {error}")
                        return LeadResponse(success=False, error=error)

                    elif response.status_code == 401:
                        # Unauthorized - don't retry
                        logger.error("CRM API authentication failed (401)")
                        return LeadResponse(success=False, error="Authentication failed")

                    elif response.status_code >= 500:
                        # Server error - retry
                        logger.warning(f"CRM API server error (attempt {attempt}/{self.max_retries}): {response.status_code}")

                        if attempt < self.max_retries:
                            # Exponential backoff: 1s, 2s, 4s
                            import asyncio
                            await asyncio.sleep(2 ** (attempt - 1))
                            continue
                        else:
                            return LeadResponse(
                                success=False,
                                error="CRM service temporarily unavailable"
                            )

                    else:
                        # Other errors
                        logger.error(f"Unexpected CRM API response: {response.status_code}")
                        return LeadResponse(
                            success=False,
                            error=f"Unexpected error (status {response.status_code})"
                        )

            except httpx.TimeoutException:
                logger.warning(f"CRM API timeout (attempt {attempt}/{self.max_retries})")
                if attempt < self.max_retries:
                    import asyncio
                    await asyncio.sleep(2 ** (attempt - 1))
                    continue
                else:
                    return LeadResponse(success=False, error="CRM service timeout")

            except httpx.RequestError as e:
                logger.error(f"CRM API request error: {e}")
                return LeadResponse(success=False, error="Failed to connect to CRM service")

        # Should not reach here, but just in case
        return LeadResponse(success=False, error="Lead creation failed after retries")
