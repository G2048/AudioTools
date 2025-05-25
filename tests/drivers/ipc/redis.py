import time
import unittest
import uuid

from app.configs.settings import get_redis_ipc_settings
from app.drivers.ipc.redis_ipc import RedisIPC, RedisMessage, TTLNotProvided


class TestRedisIPC(unittest.TestCase):
    def setUp(self):
        config = get_redis_ipc_settings()
        self.client = RedisIPC(config)
        self.message = RedisMessage(key="test_key", value="test_value")

    def test_redis_ipc(self):
        ping_response = self.client.ping()
        print(f"ping_response: {ping_response}")
        self.assertTrue(ping_response)

        # self.assertIsNotNone(self.client.getall("test_key"))

        with self.assertRaises(TTLNotProvided):
            self.client.setx(self.message)

        self.message.ttl = 10
        set_response = self.client.setx(self.message)
        self.assertTrue(set_response)
        print(f"Key: {self.message.key}, set_response: {set_response}")

    def test_get(self):
        value = {"task_id": uuid.uuid1().hex, "recognizer": "whisper"}
        # value = pickle.dumps(value)

        self.message.value = value
        self.message.ttl = 10
        message_json = self.message.model_dump_json()
        print(f"Message JSON: {message_json}")
        print()

        set_response = self.client.setx(self.message)
        self.assertTrue(set_response)
        print(f"Key: {self.message.key}, set_response: {set_response}")

        response_message = self.client.get(self.message.key)
        print(f"Response message: {response_message}")
        self.assertIsInstance(response_message, RedisMessage)
        self.assertEqual(response_message.key, self.message.key)
        self.assertEqual(response_message.value, self.message.value)
        self.assertEqual(response_message.ttl, self.message.ttl)
        print()

        response_message = self.client.get("NON EXISTING KEY")
        print(f"Response message: {response_message}")
        self.assertIsInstance(response_message, RedisMessage)
        self.assertIsNone(response_message.value)
        print()

        self.message.key = "STRING KEY"
        self.message.value = "STRING KEY"
        set_response = self.client.setx(self.message)
        self.assertTrue(set_response)
        response_message = self.client.get(self.message.key)
        print(f"Response message: {response_message}")
        self.assertIsInstance(response_message, RedisMessage)
        self.assertEqual(response_message.key, self.message.key)
        self.assertEqual(response_message.value, self.message.value)
        self.assertEqual(response_message.ttl, self.message.ttl)

    def test_check_ttl_key(self):
        self.message.ttl = 3
        self.message.key = "Check TTL Key"
        set_response = self.client.setx(self.message)

        current_ttl = self.client.check_ttl_key(self.message.key)
        while current_ttl != -2:
            print(f"Current TTL: {current_ttl}")
            current_ttl = self.client.check_ttl_key(self.message.key)
            time.sleep(1)
