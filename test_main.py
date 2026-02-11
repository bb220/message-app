import pytest
from main import verify_api_key, settings, HTTPException

@pytest.mark.asyncio
async def test_verify_api_key_valid(monkeypatch):
    # Mock settings with a valid API key
    monkeypatch.setattr(settings, "api_key", "valid_api_key")
    
    # Call the function with the correct API key
    result = await verify_api_key(x_api_key="valid_api_key")
    assert result == "valid_api_key"

@pytest.mark.asyncio
async def test_verify_api_key_invalid(monkeypatch):
    # Mock settings with a valid API key
    monkeypatch.setattr(settings, "api_key", "valid_api_key")
    
    # Call the function with an incorrect API key and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key="invalid_api_key")
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid API Key"

@pytest.mark.asyncio
async def test_verify_api_key_not_configured(monkeypatch):
    # Mock settings with no API Key configured
    monkeypatch.setattr(settings, "api_key", None)

    # Call the function and expect an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await verify_api_key(x_api_key="any_api_key")

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "API Key not configured on server"