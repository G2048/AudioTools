import logging
import os
import unittest

os.environ["JWT_SECRET_KEY"] = "test_secret_key"

from fastapi.testclient import TestClient

from app.api.models import Token, UserLogin
from app.main import app
from app.services.jwt import JWT

logger = logging.getLogger("asyncio")
logger.propagate = False
logger.setLevel(logging.CRITICAL)


class LoginTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)
        # cls.jwt_settings = JwtSettings(secret_key="test_secret_key")

    def setUp(self) -> None:
        self.user_body = UserLogin(username="admin", password="admin").model_dump_json()

    def test_login_post(self):
        response = self.client.post("/api/v1/login", data=self.user_body)
        self.assertEqual(response.status_code, 200)
        token_json = response.json()
        self.assertIsInstance(token_json, dict)
        self.assertEqual(token_json["token_type"], "bearer")
        token = Token(access_token=token_json["access_token"], token_type=token_json["token_type"])
        print(f"{token=}")
        return token

    def test_check_login_get(self):
        response = self.client.post("/api/v1/login", data=self.user_body)
        token_json = response.json()
        response = self.client.get(
            "/api/v1/login", headers={"Authorization": f"Bearer {token_json['access_token']}"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["logged_in"], True)

        fail_token = "fail_token"
        wrong_response = self.client.get(
            "/api/v1/login",
            headers={"Authorization": f"Bearer {fail_token}"},
        )
        self.assertEqual(wrong_response.status_code, 401)
        self.assertEqual(wrong_response.json()["detail"], "Invalid token")

    def test_check_login_expired_token(self):
        token = JWT().generate_token({"username": "admin"}, live_days=0)

        wrong_response = self.client.get("/api/v1/login", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(wrong_response.status_code, 401)
        self.assertEqual(wrong_response.json()["detail"], "Token expired")


if __name__ == "__main__":
    unittest.main(verbosity=2)
