import time
import unittest

from app.configs.settings import get_redis_ipc_settings
from app.drivers.ipc.redis.storages import (
    ConnectionUnavailable,
    DeleteStatus,
    DictStore,
    HashStore,
    RedisConnection,
    SetStore,
    SortedSet,
    SortedSetStore,
)
from app.drivers.ipc.redis_ipc import RedisMessage


class TestRedisConnection(unittest.TestCase):
    @unittest.expectedFailure
    def test_connection(self):
        config = get_redis_ipc_settings()
        with self.assertRaises(ConnectionUnavailable):
            connection = RedisConnection(config)
        return connection


class TestDictStore(unittest.TestCase):
    def setUp(self):
        config = get_redis_ipc_settings()
        self.connection = RedisConnection(config)
        self.store = DictStore(self.connection)
        self.message = RedisMessage(
            key=f"test_{self.store.name}_key",
            value=f"test_{self.store.name}_value",
            ttl=5,
        )
        self.assertEqual(self.store.name, "DictStore")
        self.store.delete(self.message.key)

    def test_set_and_get(self):
        self.store.set(self.message.key, self.message.value, self.message.ttl)
        response = self.store.get(self.message.key)
        self.assertEqual(response, self.message.value)

        ttl = self.store.ttl(self.message.key)
        self.assertEqual(ttl, self.message.ttl)
        while ttl > 0:
            ttl = self.store.ttl(self.message.key)
            time.sleep(1)
        self.store.delete(self.message.key)

    def test_all(self):
        self.store.set(self.message.key, self.message.value, self.message.ttl)
        store_all = self.store.all()
        print(f"Store all: {store_all=}")
        self.assertIn(self.message.key, store_all)
        for key in store_all:
            self.assertIsNotNone(key)
            self.assertIsInstance(key, str)


class TestHashStore(unittest.TestCase):
    def setUp(self):
        config = get_redis_ipc_settings()
        self.connection = RedisConnection(config)
        self.store = HashStore(self.connection)
        self.message = RedisMessage(
            key=f"test_{self.store.name}_key",
            value=f"test_{self.store.name}_value",
            ttl=5,
        )

    def tearDown(self):
        self.store.delete(self.message.key)

    def test_set(self):
        success = self.store.set(
            self.message.key,
            mapping=self.message.model_dump(exclude={"key", "ttl"}),
        )
        self.assertTrue(success)

    def test_get(self):
        self.test_set()
        print()
        response = self.store.get(self.message.key, "value")
        print(f"Get response: {response=}")
        self.assertEqual(response, self.message.value)

    def test_set_key_ttl(self):
        self.test_get()
        self.message.ttl = 5
        self.store.set_key_ttl(self.message.key, self.message.ttl)
        response = self.store.get(self.message.key, "value")
        print(f"Get response: {response=}")
        ttl = self.store.ttl(self.message.key)
        self.assertGreater(ttl, 0)

    def test_ttl(self):
        ttl = self.store.ttl(self.message.key)
        while ttl > 0:
            ttl = self.store.ttl(self.message.key)
            time.sleep(1)
            print(f"TTL: {ttl}")

        del_resp = self.store.delete(self.message.key)
        self.assertEqual(del_resp, DeleteStatus.NOT_FOUND)

    def test_touch(self):
        self.message.ttl = None
        self.test_set()
        response = self.store.get(self.message.key, "value")
        print(f"Response: {response}")
        self.assertEqual(response, self.message.value)

        new_ttl = 200
        old_ttl = self.store.fields_ttl(self.message.key, ("value",))
        res = self.store.touch(self.message.key, ("value",), ttl=new_ttl)
        print(f"Touch response: {res}")
        self.assertIsInstance(res, str)
        self.assertEqual(res, self.message.value)

        current_ttl = self.store.fields_ttl(self.message.key, ("value",))
        self.assertIsInstance(current_ttl, list)
        print(f"Current TTL: {current_ttl}")
        self.assertGreater(current_ttl, old_ttl)

        ttl = self.store.fttl(self.message.key, "value")
        self.assertEqual(ttl, new_ttl)
        print(f"Current TTL: {ttl}")

    def test_all(self):
        test_messages = (
            {
                "key": "First Test Message",
                "value": {"value": "Value of the First Test Message"},
                "ttl": None,
            },
            {
                "key": "Second Test Message",
                "value": {"value": "Value of the Second Test Message"},
                "ttl": None,
            },
        )

        for message in test_messages:
            self.store.set(message["key"], mapping=message["value"])
            store_all = self.store.all(message["key"])
            print(f"Store all: {store_all=}")
            self.assertEqual(message["value"], store_all)
            for key in store_all:
                self.assertIsNotNone(key)
                self.assertIsInstance(key, str)

    def test_getall(self):
        test_messages = (
            {
                "key": "First Test Message",
                "value": {"value": "Value of the First Test Message"},
                "ttl": None,
            },
            {
                "key": "Second Test Message",
                "value": {"value": "Value of the Second Test Message"},
                "ttl": None,
            },
        )

        for message in test_messages:
            self.store.set(message["key"], mapping=message["value"])

            store_all = self.store.getall(message["key"])
            print(f"Store all: {store_all=}")
            self.assertEqual(message["value"], store_all)
            for key in store_all:
                self.assertIsNotNone(key)
                self.assertIsInstance(key, str)


class TestSetStore(unittest.TestCase):
    def setUp(self):
        config = get_redis_ipc_settings()
        self.connection = RedisConnection(config)
        self.store = SetStore(self.connection)
        self.message = RedisMessage(
            key=f"test_{self.store.name}_key",
            value=f"test_{self.store.name}_value",
            ttl=5,
        )

    def tearDown(self):
        self.store.delete(self.message.key)

    def test_set(self):
        value = self.message.model_dump(exclude={"key", "ttl"})
        print(f"{value=}")
        success = self.store.set(
            self.message.key,
            mapping=value,
        )
        self.assertTrue(success)
        store_all = self.store.all(self.message.key)
        self.assertIsInstance(store_all, list)
        print(f"Store all: {store_all=}")

    @unittest.skip("Not implementing the .get()")
    def test_get(self):
        self.test_set()
        print()
        response = self.store.get(self.message.key, "value")
        print(f"Get response: {response=}")
        self.assertEqual(response, self.message.value)

    def test_all(self):
        test_messages = (
            {
                "key": "First_Test_Message",
                "value": {"value": "Value of the First Test Message"},
                "ttl": None,
            },
            {
                "key": "Second_Test_Message",
                "value": {"value": "Value of the Second Test Message"},
                "ttl": None,
            },
        )

        try:
            for message in test_messages:
                print(f"Key: {message['key']}")
                print(f"Value: {message['value']}")
                success = self.store.set(message["key"], ("value1", "value2"))
                self.assertTrue(success)
            all = self.store.all(message["key"])
            print(f"{all=}")
            self.assertIsInstance(all, list)
            self.assertIsInstance(all[0], str)
            self.assertIsInstance(all[-1], str)

        finally:
            for message in test_messages:
                self.store.delete(message["key"])


class TesSortedSetStore(unittest.TestCase):
    def setUp(self):
        config = get_redis_ipc_settings()
        self.connection = RedisConnection(config)
        self.store = SortedSetStore(self.connection)
        self.message = RedisMessage(
            key=f"test_{self.store.name}_key",
            value=12,
            ttl=5,
        )

    def tearDown(self):
        self.store.delete(self.message.key)

    def test_set(self):
        value = self.message.model_dump(exclude={"key", "ttl"})
        print(f"{value=}")
        success = self.store.set(
            self.message.key,
            mapping=value,
        )
        self.assertTrue(success)
        store_all = self.store.all(self.message.key)
        self.assertIsInstance(store_all, list)
        print(f"Store all: {store_all=}")

    @unittest.skip("Not implementing the .get()")
    def test_get(self):
        self.test_set()
        response = self.store.get(self.message.key, "value")
        print(f"Get response: {response=}")
        self.assertEqual(response, self.message.value)

    def test_all(self):
        test_messages = (
            {
                "key": "First_Test_Message",
                "value": {"Value of the First Test Message": 1},
                "ttl": None,
            },
            {
                "key": "Second_Test_Message",
                "value": {"Value of the Second Test Message": 2},
                "ttl": None,
            },
        )

        print()
        try:
            for message in test_messages:
                success = self.store.set(message["key"], message["value"])
                self.assertTrue(success)
            all = self.store.all(message["key"])
            print(f"{all=}")
            self.assertIsNotNone(all)
            self.assertIsInstance(all, SortedSet)
            pair = all.pairs[0]
            print(f"{pair=}")
            self.assertIsInstance(pair, tuple)
            self.assertIsInstance(pair[0], str)
            self.assertIsInstance(pair[-1], float)
        finally:
            for message in test_messages:
                self.store.delete(message["key"])
