from app.config import Settings, settings
from app.services.llm_service import LLMService, llm_service
from app.services.memory_service import MemoryService, memory_service


def get_settings() -> Settings:
    return settings


def get_llm_service() -> LLMService:
    return llm_service


def get_memory_service() -> MemoryService:
    return memory_service
