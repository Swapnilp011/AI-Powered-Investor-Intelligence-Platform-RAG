import json
import os
import re
import time
from typing import Type
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


def get_llm_provider() -> str:
    """Get configured LLM provider (gemini, ollama, openai)."""
    return os.getenv("LLM_PROVIDER", "gemini").lower()


class RateLimitedGeminiEmbeddings:
    """
    Wrapper around GoogleGenerativeAIEmbeddings with batching, rate-limiting retry logic,
    pacing delays, and guaranteed output length matching len(texts).
    """
    def __init__(self, model: str, google_api_key: str):
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        self._embeddings = GoogleGenerativeAIEmbeddings(
            model=model,
            google_api_key=google_api_key
        )

    def embed_query(self, text: str) -> list[float]:
        for attempt in range(5):
            try:
                return self._embeddings.embed_query(text)
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "Quota" in err_str:
                    sleep_sec = 3 * (attempt + 1)
                    print(f"[rate-limit] Gemini embedding query rate limit hit. Waiting {sleep_sec}s...")
                    time.sleep(sleep_sec)
                else:
                    raise e
        return [0.0] * 3072

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        results = []
        batch_size = 20
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            batch_success = False

            for attempt in range(5):
                try:
                    batch_embeddings = self._embeddings.embed_documents(batch)
                    if len(batch_embeddings) == len(batch):
                        results.extend(batch_embeddings)
                        batch_success = True
                        break
                except Exception as e:
                    err_str = str(e)
                    if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "Quota" in err_str:
                        sleep_sec = 4 * (attempt + 1)
                        print(f"[rate-limit] Gemini embedding rate limit hit (429) on batch {batch_num}/{total_batches}. Retrying in {sleep_sec}s...")
                        time.sleep(sleep_sec)
                    else:
                        print(f"[warning] Embedding batch failed: {e}")
                        time.sleep(2)

            if not batch_success:
                # If batch failed after retries, fallback to item-by-item processing
                for text_item in batch:
                    item_success = False
                    for attempt in range(3):
                        try:
                            vec = self._embeddings.embed_query(text_item)
                            results.append(vec)
                            item_success = True
                            break
                        except Exception:
                            time.sleep(2)
                    if not item_success:
                        fallback_vec = results[-1] if results else [0.0] * 3072
                        results.append(fallback_vec)
            
            # Pacing pause to comply with Google AI Studio 15 RPM free-tier limit
            if i + batch_size < len(texts):
                time.sleep(1.2)

        # Guarantee exact length match
        while len(results) < len(texts):
            results.append(results[-1] if results else [0.0] * 3072)
        return results[:len(texts)]


def get_embedding_client():
    """
    Returns an embedding model client conforming to the LangChain Embeddings interface.
    Supports Google Gemini, Ollama, and OpenAI.
    """
    provider = get_llm_provider()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment variables.")
        embed_model = os.getenv("GEMINI_EMBED_MODEL", "gemini-embedding-001")
        if embed_model.startswith("models/"):
            embed_model = embed_model.replace("models/", "")

        return RateLimitedGeminiEmbeddings(
            model=embed_model,
            google_api_key=api_key
        )

    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
        from langchain_ollama import OllamaEmbeddings
        return OllamaEmbeddings(
            base_url=base_url,
            model=embed_model
        )

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set in environment variables.")
        embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(
            model=embed_model,
            api_key=api_key
        )

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def get_llm_completion(prompt: str, system_prompt: str = "You are an expert financial analyst.") -> str:
    """
    Generate text response from the configured LLM provider.
    """
    provider = get_llm_provider()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment variables.")
        chat_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash")
        if chat_model.startswith("models/"):
            chat_model = chat_model.replace("models/", "")

        for attempt in range(5):
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=chat_model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt
                    )
                )
                return response.text or ""
            except Exception as e:
                err_str = str(e)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "Quota" in err_str:
                    sleep_sec = 4 * (attempt + 1)
                    print(f"[rate-limit] Gemini chat API rate limit hit (429). Retrying in {sleep_sec}s...")
                    time.sleep(sleep_sec)
                else:
                    try:
                        from langchain_google_genai import ChatGoogleGenerativeAI
                        llm = ChatGoogleGenerativeAI(
                            model=chat_model,
                            google_api_key=api_key
                        )
                        res = llm.invoke(f"{system_prompt}\n\n{prompt}")
                        return str(res.content)
                    except Exception:
                        raise e
        return ""

    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        chat_model = os.getenv("OLLAMA_CHAT_MODEL", "llama3")
        from langchain_ollama import ChatOllama
        llm = ChatOllama(
            base_url=base_url,
            model=chat_model
        )
        res = llm.invoke(f"{system_prompt}\n\n{prompt}")
        return str(res.content)

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o")
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content or ""

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def get_structured_completion(
    prompt: str,
    response_model: Type[BaseModel]
) -> BaseModel:
    """
    Generate structured Pydantic model response from the configured LLM provider.
    Supports JSON output generation and schema validation.
    """
    provider = get_llm_provider()
    json_prompt = (
        f"{prompt}\n\n"
        "IMPORTANT: You MUST respond ONLY with a valid JSON object matching the requested schema. "
        "Do not include markdown code block formatting like ```json ... ``` unless required. "
        "Return raw JSON."
    )

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set in environment variables.")
        chat_model = os.getenv("GEMINI_CHAT_MODEL", "gemini-3.6-flash")
        if chat_model.startswith("models/"):
            chat_model = chat_model.replace("models/", "")

        raw_text = None
        for attempt in range(5):
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model=chat_model,
                    contents=json_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are an expert financial analyst. Respond ONLY with valid JSON.",
                        response_mime_type="application/json"
                    )
                )
                raw_text = response.text or "{}"
                break
            except Exception as exc:
                err_str = str(exc)
                if "RESOURCE_EXHAUSTED" in err_str or "429" in err_str or "Quota" in err_str:
                    sleep_sec = 4 * (attempt + 1)
                    print(f"[rate-limit] Gemini structured output rate limit hit (429). Retrying in {sleep_sec}s...")
                    time.sleep(sleep_sec)
                else:
                    raw_text = get_llm_completion(json_prompt)
                    break
        if raw_text is None:
            raw_text = get_llm_completion(json_prompt)

    else:
        raw_text = get_llm_completion(json_prompt)

    clean_text = raw_text.strip()
    if clean_text.startswith("```"):
        clean_text = re.sub(r"^```(?:json)?\n?", "", clean_text)
        clean_text = re.sub(r"\n?```$", "", clean_text).strip()

    match = re.search(r"\{.*\}", clean_text, re.DOTALL)
    if match:
        clean_text = match.group(0)

    try:
        if hasattr(response_model, "model_validate_json"):
            return response_model.model_validate_json(clean_text)
        else:
            return response_model.parse_raw(clean_text)
    except Exception as exc:
        print(f"[warning] Structured JSON validation error: {exc}. Raw text: {raw_text}")
        if hasattr(response_model, "model_construct"):
            return response_model.model_construct()
        return response_model()
