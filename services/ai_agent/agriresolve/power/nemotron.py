"""
NVIDIA Nemotron / Meterless Power Layer Client for AgriResolve.
Connects to NVIDIA NIM / Meterless OpenAI-compatible inference endpoints.
Never prints or leaks secrets in logs or exceptions.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Optional
from ..config import PowerLayerConfig
from .base import PowerLayerClient, PowerLayerNotConfiguredError


class NemotronPowerClient(PowerLayerClient):
    """
    Client for NVIDIA Nemotron (e.g. nvidia/nemotron-4-340b-instruct) via NVIDIA NIM or Meterless.
    """

    def __init__(self, config: PowerLayerConfig):
        self.config = config

    def is_available(self) -> bool:
        return self.config.is_configured

    def generate_reasoning(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 2048,
    ) -> str:
        """
        Sends request to NVIDIA NIM / Meterless chat completions endpoint.
        """
        if not self.is_available():
            raise PowerLayerNotConfiguredError()

        base_url = self.config.base_url.rstrip("/")
        # NVIDIA NIM / OpenAI compatible completions endpoint
        url = f"{base_url}/chat/completions"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 0.95,
        }

        data_bytes = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "User-Agent": "AgriResolve-Nemotron-Client/0.1.0",
        }

        req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=self.config.timeout_seconds) as response:
                result_json = json.loads(response.read().decode("utf-8"))
                choices = result_json.get("choices", [])
                if choices and "message" in choices[0]:
                    return choices[0]["message"].get("content", "")
                return ""
        except urllib.error.HTTPError as e:
            status = e.code
            err_msg = f"NVIDIA/Meterless API HTTP error {status}: {e.reason}"
            if status == 401:
                err_msg += " (Authentication failed. Please verify NVIDIA_API_KEY in .env)"
            elif status == 429:
                err_msg += " (Rate limit or quota exceeded on model endpoint)"
            raise RuntimeError(err_msg)
        except urllib.error.URLError as e:
            raise RuntimeError(f"Network failure connecting to NVIDIA Nemotron endpoint: {e.reason}")
        except TimeoutError:
            raise RuntimeError(f"Nemotron inference call timed out after {self.config.timeout_seconds} seconds")
