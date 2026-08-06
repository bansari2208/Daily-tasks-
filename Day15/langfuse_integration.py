import os
import time
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from langfuse import Langfuse, observe

# Load environment variables from Day15/.env and root .env
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class LangfusePromptManager:
    """
    Day 15 Langfuse Prompt Registry & SDK Integration Manager.
    
    Conforms strictly to official Langfuse Python SDK v4.14.1 specification.
    Target prompt name in Langfuse Cloud: 'ticket_classifier 1'.
    """

    def __init__(
        self,
        public_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        host: Optional[str] = None
    ):
        self.public_key = public_key or os.getenv("LANGFUSE_PUBLIC_KEY")
        self.secret_key = secret_key or os.getenv("LANGFUSE_SECRET_KEY")
        self.host = (
            host
            or os.getenv("LANGFUSE_HOST")
            or os.getenv("LANGFUSE_BASE_URL")
            or os.getenv("LANGFUSE_BASEURL")
            or "https://cloud.langfuse.com"
        )

        # Set environment variables for Langfuse SDK and OpenTelemetry Exporter
        os.environ["LANGFUSE_HOST"] = self.host
        os.environ["LANGFUSE_BASE_URL"] = self.host
        if self.public_key:
            os.environ["LANGFUSE_PUBLIC_KEY"] = self.public_key
        if self.secret_key:
            os.environ["LANGFUSE_SECRET_KEY"] = self.secret_key

        if not self.public_key or not self.secret_key:
            raise ValueError(
                "Langfuse credentials missing! Ensure LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY "
                "are configured in environment or Day15/.env file."
            )

        print("\n========== LANGFUSE CLIENT INIT ==========")
        print("Host       :", self.host)
        print("Public Key :", self.public_key[:12] + "...")
        print("==========================================\n")

        # Initialize official Langfuse client (v4.14.1)
        self.client = Langfuse(
            public_key=self.public_key,
            secret_key=self.secret_key,
            host=self.host
        )

    def _log_debug_prompt_info(self, req_name: str, req_version: Optional[int], req_label: Optional[str], prompt_obj: Any):
        """Debug logging before returning prompt object as required by Requirement 5."""
        print("-" * 35)
        print(f"Requested Prompt Name : {req_name}")
        print(f"Requested Version     : {req_version}")
        print(f"Requested Label       : {req_label}")
        print(f"Returned Prompt Name  : {getattr(prompt_obj, 'name', None)}")
        print(f"Returned Version      : {getattr(prompt_obj, 'version', None)}")
        print(f"Returned Labels       : {getattr(prompt_obj, 'labels', None)}")
        print("-" * 35)

    def get_prompt_by_name(self, prompt_name: str = "ticket_classifier 1"):
        """
        Retrieves a prompt from Langfuse registry by name (fetches latest version).
        """
        prompt_obj = self.client.get_prompt(prompt_name)
        self._log_debug_prompt_info(prompt_name, req_version=None, req_label="latest", prompt_obj=prompt_obj)
        return prompt_obj

    def get_prompt_by_version(self, prompt_name: str = "ticket_classifier 1", version: int = 1):
        """
        Retrieves a specific version of a prompt from Langfuse registry.
        No silent fallback — surfaces actual SDK exceptions if version is missing.
        """
        prompt_obj = self.client.get_prompt(prompt_name, version=version)
        self._log_debug_prompt_info(prompt_name, req_version=version, req_label=None, prompt_obj=prompt_obj)
        return prompt_obj

    def get_prompt_by_label(self, prompt_name: str = "ticket_classifier 1", label: str = "production"):
        """
        Retrieves a prompt by production or environment label from Langfuse registry.
        """
        prompt_obj = self.client.get_prompt(prompt_name, label=label)
        self._log_debug_prompt_info(prompt_name, req_version=None, req_label=label, prompt_obj=prompt_obj)
        return prompt_obj

    def compile_prompt(self, prompt_obj: Any, ticket_text: str) -> str:
        """
        Compiles prompt template safely using template variables via native prompt.compile(...).
        Prevents prompt injection by isolating user input inside template variables.
        """
        if hasattr(prompt_obj, "compile"):
            try:
                return prompt_obj.compile(ticket=ticket_text)
            except Exception:
                return prompt_obj.compile(user_prompt=ticket_text)
        elif hasattr(prompt_obj, "prompt"):
            return str(prompt_obj.prompt).replace("{{ticket}}", ticket_text)
        else:
            raise TypeError(f"Provided object of type {type(prompt_obj)} is not a valid Langfuse prompt object.")

    def log_traced_generation(
        self,
        prompt_obj: Any,
        ticket_text: str,
        compiled_prompt: str,
        completion_text: str,
        model_name: str = "gpt-4.1-mini",
        prompt_tokens: int = 120,
        completion_tokens: int = 45,
        latency_ms: float = 350.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Creates an OpenTelemetry Trace & Generation linked directly to the fetched Langfuse Prompt object.
        Logs Prompt Name, Prompt Version, Model, Input, Output, Token Usage, and Latency.
        Explicitly calls .end() on the observation span so end_time is populated and Langfuse backend
        indexes the generation under Prompts -> Linked Generations.
        """
        p_name = getattr(prompt_obj, "name", "ticket_classifier 1")
        p_version = getattr(prompt_obj, "version", 1)

        obs_metadata = metadata or {}
        obs_metadata.update({
            "prompt_name": p_name,
            "prompt_version": p_version,
            "environment": os.getenv("APP_ENV", "production"),
            "latency_ms": latency_ms
        })

        # Start observation of type 'generation' linked directly to prompt_obj (v4 SDK API)
        generation = self.client.start_observation(
            name=f"llm_generation_v{p_version}",
            as_type="generation",
            model=model_name,
            prompt=prompt_obj,  # Link generation directly to the Langfuse prompt version!
            input={"compiled_prompt": compiled_prompt, "variables": {"ticket": ticket_text}},
            output={"completion": completion_text},
            usage_details={
                "input": prompt_tokens,
                "output": completion_tokens,
                "total": prompt_tokens + completion_tokens
            },
            metadata=obs_metadata
        )

        # Explicity end the generation span so end_time is set for backend indexing!
        if hasattr(generation, "end"):
            generation.end()

        # Force immediate flush to live Langfuse server
        self.client.flush()

        return {
            "observation_id": getattr(generation, "id", "live-obs-id"),
            "prompt_name": p_name,
            "prompt_version": p_version,
            "model": model_name,
            "latency_ms": latency_ms,
            "tokens": prompt_tokens + completion_tokens,
            "status": "LIVE_LANGFUSE_LOGGED"
        }