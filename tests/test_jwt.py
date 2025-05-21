import unittest

from app.services.jwt import JWT, JwtPayload


class TestJwt(unittest.TestCase):
    def setUp(self) -> None:
        self.client = JWT

    def tearDown(self) -> None:
        return super().tearDown()

    def test_JwtPayload(self):
        test_token = JwtPayload(sub="test")
        self.assertIsNotNone(test_token)
        self.assertIsInstance(test_token, JwtPayload)
        self.assertNotEqual(test_token, JwtPayload(sub="test"))

    def test_generate_token(self):
        test_token = self.client.generate_token(JwtPayload(sub="test"))
        self.assertIsNotNone(test_token)
        self.assertIsInstance(test_token, str)
        print(f"{test_token=}")

    def test_validate(self):
        test_token = self.client.generate_token(JwtPayload(sub="test"))
        token_model = self.client.validate(test_token)
        self.assertIsNotNone(token_model)
        self.assertIsInstance(token_model, JwtPayload)
        print(f"{token_model=}")

    def test_payload(self):
        test_token = self.client.generate_token(JwtPayload(sub="test"))
        token_model = self.client.payload(test_token)
        self.assertIsNotNone(token_model)
        self.assertIsInstance(token_model, JwtPayload)
        self.assertEqual(token_model.sub, "test")
        print(f"{token_model=}")
