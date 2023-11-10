from typing import Dict

from fastapi.testclient import TestClient

from app.core.config import settings
from app.tests.utils.login import sign_message, spawn_account


def test_get_access_token(client: TestClient) -> None:
    account = spawn_account()
    public_address = account.address
    r = client.post(f"{settings.API_V1_STR}/login/metamask/nonce/{public_address}")
    assert r.status_code == 200
    nonce_response = r.json()
    nonce = nonce_response["nonce"]

    r = client.post(f"{settings.API_V1_STR}/login/auth",
                    data={
                        "public_address": public_address,
                        "signed_nonce": sign_message(account, nonce)
                    })
    result = r.json()
    assert r.status_code == 200
    assert "access_token" in result


def test_use_access_token(
    client: TestClient, superuser_token_headers: Dict[str, str]
) -> None:
    r = client.post(
        f"{settings.API_V1_STR}/login/test-token", headers=superuser_token_headers,
    )
    result = r.json()
    assert r.status_code == 200
    assert "email" in result
