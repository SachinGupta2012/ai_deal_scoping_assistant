"""Live AI provider chain and cache tests."""
from app.core.config import settings
from app.services.ai.cache import get_cached, input_hash, set_cached
from app.services.ai.live_json import generate_json, live_chain


def test_live_chain_prefers_configured_provider_then_chain(monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_AI", False)
    monkeypatch.setattr(settings, "AI_PROVIDER", "openrouter")
    monkeypatch.setattr(settings, "AI_PROVIDER_CHAIN", "cloudflare,openrouter,groq,google")
    assert live_chain() == ["openrouter", "cloudflare", "groq", "google"]


def test_ai_cache_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "AI_CACHE_ENABLED", True)
    monkeypatch.setattr(settings, "AI_CACHE_DIR", str(tmp_path))
    payload_hash = input_hash("same-input")
    set_cached("extract_v1", payload_hash, "openrouter", "model-x", {"ok": True})
    assert get_cached("extract_v1", payload_hash, "openrouter", "model-x") == {"ok": True}


def test_generate_json_uses_cached_provider_payload(tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_AI", False)
    monkeypatch.setattr(settings, "AI_PROVIDER", "openrouter")
    monkeypatch.setattr(settings, "AI_PROVIDER_CHAIN", "openrouter")
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "test-key")
    monkeypatch.setattr(settings, "OPENROUTER_MODEL", "free-model")
    monkeypatch.setattr(settings, "AI_CACHE_ENABLED", True)
    monkeypatch.setattr(settings, "AI_CACHE_DIR", str(tmp_path))
    payload_hash = input_hash("payload")
    set_cached("prd_v1", payload_hash, "openrouter", "free-model", {"overview": "ok"})
    data, meta = generate_json("prd_v1", payload_hash, "system", "user")
    assert data == {"overview": "ok"}
    assert meta["provider"] == "openrouter" and meta["cache_hit"] is True


def test_generate_json_falls_back_to_next_provider(monkeypatch):
    monkeypatch.setattr(settings, "USE_MOCK_AI", False)
    monkeypatch.setattr(settings, "AI_PROVIDER", "cloudflare")
    monkeypatch.setattr(settings, "AI_PROVIDER_CHAIN", "cloudflare,openrouter")
    monkeypatch.setattr(settings, "CLOUDFLARE_ACCOUNT_ID", "acct")
    monkeypatch.setattr(settings, "CLOUDFLARE_API_TOKEN", "cf-key")
    monkeypatch.setattr(settings, "CLOUDFLARE_MODEL", "cf-model")
    monkeypatch.setattr(settings, "OPENROUTER_API_KEY", "or-key")
    monkeypatch.setattr(settings, "OPENROUTER_MODEL", "or-model")
    monkeypatch.setattr(settings, "AI_CACHE_ENABLED", False)

    def fake_call(cfg, system, user, temperature):
        if cfg.name == "cloudflare":
            raise RuntimeError("429 quota")
        return {"ok": True}

    monkeypatch.setattr("app.services.ai.live_json._call_openai", fake_call)
    data, meta = generate_json("extract_v1", input_hash("x"), "system", "user")
    assert data == {"ok": True}
    assert meta["provider"] == "openrouter"
    assert meta["attempts"][0]["provider"] == "cloudflare"
