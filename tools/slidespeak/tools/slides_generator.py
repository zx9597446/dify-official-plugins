import asyncio
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Optional, Generator
import aiohttp
from pydantic import ConfigDict
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin import Tool


class SlidesGeneratorTool(Tool):
    """
    Tool for generating presentations using the SlideSpeak API
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    headers: Optional[dict[str, str]] = None
    base_url: Optional[str] = None
    timeout: Optional[aiohttp.ClientTimeout] = None
    poll_interval: Optional[int] = None

    class TaskState(Enum):
        FAILURE = "FAILURE"
        REVOKED = "REVOKED"
        SUCCESS = "SUCCESS"
        PENDING = "PENDING"
        RECEIVED = "RECEIVED"
        STARTED = "STARTED"

    @dataclass
    class PresentationRequest:
        plain_text: str
        length: Optional[int] = None
        theme: Optional[str] = None

    async def _generate_presentation(
        self, session: aiohttp.ClientSession, request: PresentationRequest
    ) -> dict[str, Any]:
        """Generate a new presentation asynchronously"""
        async with session.post(
            f"{self.base_url}/presentation/generate", headers=self.headers, json=asdict(request), timeout=self.timeout
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def _get_task_status(self, session: aiohttp.ClientSession, task_id: str) -> dict[str, Any]:
        """Get the status of a task asynchronously"""
        async with session.get(
            f"{self.base_url}/task_status/{task_id}", headers=self.headers, timeout=self.timeout
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def _wait_for_completion(self, session: aiohttp.ClientSession, task_id: str) -> str:
        """Wait for task completion and return download URL"""
        while True:
            status = await self._get_task_status(session, task_id)
            task_status = self.TaskState(status["task_status"])
            if task_status == self.TaskState.SUCCESS:
                return status["task_result"]["url"]
            if task_status in [self.TaskState.FAILURE, self.TaskState.REVOKED]:
                raise Exception(f"Task failed with status: {task_status.value}")
            await asyncio.sleep(self.poll_interval)

    async def _generate_slides(self, plain_text: str, length: Optional[int], theme: Optional[str]) -> str:
        """Generate slides and return the download URL"""
        async with aiohttp.ClientSession() as session:
            request = self.PresentationRequest(plain_text=plain_text, length=length, theme=theme)
            result = await self._generate_presentation(session, request)
            task_id = result["task_id"]
            download_url = await self._wait_for_completion(session, task_id)
            return download_url

    async def _fetch_presentation(self, session: aiohttp.ClientSession, download_url: str) -> bytes:
        """Fetch the presentation file from the download URL"""
        async with session.get(download_url, timeout=self.timeout) as response:
            response.raise_for_status()
            return await response.read()

    def _invoke(
        self, tool_parameters: dict[str, Any]
    ) -> Generator[ToolInvokeMessage, None, None]:
        """Synchronous invoke method that runs asynchronous code"""

        async def async_invoke():
            plain_text = tool_parameters.get("plain_text", "")
            length = tool_parameters.get("length")
            theme = tool_parameters.get("theme")
            if not self.runtime or not self.runtime.credentials:
                raise ToolProviderCredentialValidationError("Tool runtime or credentials are missing")
            api_key = self.runtime.credentials.get("slidespeak_api_key")
            if not api_key:
                raise ToolProviderCredentialValidationError("SlideSpeak API key is missing")
            self.headers = {"Content-Type": "application/json", "X-API-Key": api_key}
            self.base_url = "https://api.slidespeak.co/api/v1"
            self.timeout = aiohttp.ClientTimeout(total=30)
            self.poll_interval = 2
            try:
                download_url = await self._generate_slides(plain_text, length, theme)
                async with aiohttp.ClientSession() as session:
                    presentation_bytes = await self._fetch_presentation(session, download_url)
                return [
                    self.create_text_message(download_url),
                    self.create_blob_message(
                        blob=presentation_bytes,
                        meta={"mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation"},
                    ),
                ]
            except Exception as e:
                return [self.create_text_message(f"An error occurred: {str(e)}")]

        messages = asyncio.run(async_invoke())
        for message in messages:
            yield message
