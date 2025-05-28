import logging

from app.configs.settings import get_redis_ipc_settings
from app.drivers.ipc.redis import HashStore, RedisConnection, RedisException
from app.interfaces.storages import ITaskStorage, Task_id, TaskMessage, TTLTaskId

logger = logging.getLogger("app.adapters.storages")


class StorageException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class TaskIdNotFoundError(StorageException):
    pass


class RedisTaskStorage(ITaskStorage):
    TASKS_KEY = "TASKS_ID"
    TASK_TTL = TTLTaskId

    def __init__(self):
        try:
            config = get_redis_ipc_settings()
            self.store = HashStore(RedisConnection(config))
        except RedisException as e:
            raise StorageException(e.detail)

    def set(self, message: TaskMessage) -> bool:
        logger.info(f"Set Task_id: {message.task_id} -> {message.recognizer}")
        success = self.store.set(message.task_id, mapping=message.model_dump())
        self.store.set_key_ttl(message.task_id, self.TASK_TTL)

        ttl = self.store.ttl(message.task_id)
        logger.info(f"TTL Task_id: {message.task_id} -> {ttl}")

        logger.info(f"Write {message.task_id} to {self.TASKS_KEY}")

        self.store.set(self.TASKS_KEY, {message.task_id: message.task_id})
        self.store.set_fttl(self.TASKS_KEY, message.task_id, self.TASK_TTL)
        fttl = self.store.fttl(message.task_id, message.task_id)
        logger.info(f"FTTL Task_id: {message.task_id} -> {fttl}")
        return bool(success)

    def get(self, task_id: Task_id) -> TaskMessage | None:
        logger.info(f"Get Task_id: {task_id}")
        message = self.store.all(task_id)
        logger.debug(f"Response TaskMessage: {message}")
        if not message:
            raise TaskIdNotFoundError(f"Task_id: {task_id} not found")
        return TaskMessage.model_validate(message)

    def list(self) -> list[TaskMessage] | None:
        messages = self.store.all(self.TASKS_KEY)
        logger.debug(f"Response TaskMessage: {messages}")
        if not messages:
            return []
        return [self.get(task_id) for task_id in messages]
