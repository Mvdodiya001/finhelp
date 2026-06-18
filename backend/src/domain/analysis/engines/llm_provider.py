"""
LLM Provider — Concrete implementation of the ILLMProvider interface.

Wraps a locally-hosted GGUF model (default: Gemma 2B) loaded via llama.cpp.
The model is lazy-loaded on first use and cached for subsequent calls.

Follows:
  - Single Responsibility: Only handles LLM sentiment analysis.
  - Open/Closed: New LLM providers (OpenAI, Anthropic) can implement ILLMProvider
    without modifying this module.
  - Dependency Inversion: Depends on the ILLMProvider abstraction.
"""

import json
from typing import Optional

from huggingface_hub import hf_hub_download
from llama_cpp import Llama

from src.core.interfaces import ILLMProvider
from src.domain.analysis.schemas import SentimentResult
from src.core.logger import get_logger

logger = get_logger(__name__)


class LocalLLMProvider(ILLMProvider):
    """Analyzes news sentiment using a locally-hosted GGUF language model.

    The model binary is downloaded from Hugging Face Hub on first use and
    loaded into ``llama.cpp``. Subsequent calls reuse the already-loaded
    model instance.

    Args:
        repo_id: Hugging Face repository ID for the GGUF model.
        filename: Filename of the quantized GGUF file inside the repo.

    Attributes:
        _repo_id: HF repo identifier.
        _filename: GGUF file to download.
        _revision: Model revision commit hash.
        _llm: Lazily-initialized :class:`llama_cpp.Llama` instance.
    """

    def __init__(
        self,
        repo_id: str = "bartowski/gemma-2-2b-it-GGUF",
        filename: str = "gemma-2-2b-it-Q4_K_M.gguf",
        revision: str = "855f67caed130e1befc571b52bd181be2e858883",
    ) -> None:
        """Initialize provider metadata without loading the model.

        Args:
            repo_id: Hugging Face Hub repository ID.
            filename: Name of the GGUF model file to download.
            revision: Commit hash to pin the model version.
        """
        self._repo_id: str = repo_id
        self._filename: str = filename
        self._revision: str = revision
        self._llm: Optional[Llama] = None

    def _ensure_model_loaded(self) -> Llama:
        """Lazy-load the GGUF model on first invocation.

        Downloads the model file from Hugging Face Hub (if not already
        cached locally) and initialises a ``llama_cpp.Llama`` instance
        with a 2048-token context window.

        Returns:
            The ready-to-use :class:`llama_cpp.Llama` instance.
        """
        if self._llm is None:
            model_path: str = hf_hub_download(
                repo_id=self._repo_id,
                filename=self._filename,
                revision=self._revision,
                local_dir="models",
            )
            logger.info("Model ready at %s. Initializing llama.cpp...", model_path)
            self._llm = Llama(
                model_path=model_path,
                n_ctx=2048,
                verbose=False,
            )
        return self._llm

    def analyze_sentiment(self, headlines: list[str]) -> SentimentResult:
        """Run LLM-based sentiment analysis on the provided headlines.

        Constructs a financial-analyst prompt, sends it to the local model
        using ChatML format with constrained JSON output, and parses the
        structured response.

        The sentiment score is clamped to the ``[-10, 10]`` range as a
        safety measure against out-of-range model outputs.

        Args:
            headlines: List of formatted news headline strings to analyze.

        Returns:
            A :class:`SentimentResult` containing the integer score,
            text summary, raw headlines, and the provider name.
        """
        if not headlines:
            logger.warning("No headlines provided; returning neutral sentiment.")
            return SentimentResult(
                score=0,
                summary="No news found for analysis.",
                headlines=[],
                provider_used="LocalLLM",
            )

        llm: Llama = self._ensure_model_loaded()
        news_text: str = "\n".join([f"- {h}" for h in headlines])

        prompt: str = (
            "You are a financial analyst. Analyze these recent news headlines:\n"
            f"{news_text}\n\n"
            "Output ONLY a JSON object with 'score' (integer from -10 to +10, "
            "where -10 is very bearish and 10 is very bullish) and 'summary' "
            "(brief text explanation)."
        )

        try:
            response = llm.create_chat_completion(
                messages=[{"role": "user", "content": prompt}],
                response_format={
                    "type": "json_object",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "score": {"type": "integer"},
                            "summary": {"type": "string"},
                        },
                        "required": ["score", "summary"],
                    },
                },
                temperature=0.1,
            )

            content: str = response["choices"][0]["message"]["content"]
            result: dict = json.loads(content)

            # Clamp score to valid range
            score: int = max(-10, min(10, int(result.get("score", 0))))
            summary: str = result.get("summary", "")

            logger.info("LLM sentiment score for headlines: %d", score)

            return SentimentResult(
                score=score,
                summary=summary,
                headlines=headlines,
                provider_used="LocalLLM",
            )

        except Exception as exc:
            logger.error("Local LLM error: %s", exc)
            return SentimentResult(
                score=0,
                summary=f"Local LLM Error: {exc}",
                headlines=headlines,
                provider_used="LocalLLM",
            )
