import time
from fastapi import Depends
from src.core.cache import InMemoryCacheService
from src.domain.analysis.engines.data_engine import DataEngine
from src.domain.analysis.engines.fusion_engine import FusionEngine
from src.domain.analysis.engines.news_providers import FallbackNewsProvider
from src.domain.analysis.engines.llm_provider import LocalLLMProvider
from src.domain.analysis.engines.ml_engine import EnsembleStrategy
from src.core.logger import get_logger

logger = get_logger(__name__)

class ServiceContainer:
    """Composition root that wires every concrete implementation.

    Instantiated **once** at module level so that FastAPI ``Depends()`` can
    inject the same container into every request handler.
    """
    def __init__(self) -> None:
        """Create and wire all service implementations."""
        logger.info("Initialising ServiceContainer …")
        self.data_engine = DataEngine()
        self.ml_strategy = EnsembleStrategy()
        self.news_provider = FallbackNewsProvider()
        self.llm_provider = LocalLLMProvider()
        self.fusion_engine = FusionEngine()
        self.cache = InMemoryCacheService()
        self.start_time: float = time.time()
        logger.info("ServiceContainer ready")

# Module-level singleton
_container = ServiceContainer()

def get_container() -> ServiceContainer:
    """Dependency injection provider for the ServiceContainer."""
    return _container
