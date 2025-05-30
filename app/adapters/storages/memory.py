import logging

from app.configs.settings import get_redis_ipc_settings
from app.drivers.ipc.redis import HashStore, RedisConnection, RedisException
from app.interfaces.recognizers import IRecognitionStorage, TaskIdStatus
from app.interfaces.storages import (
    ITaskStorage,
    Task_id,
    TaskMessage,
    TTLTaskId,
)

logger = logging.getLogger("app.adapters.storages")


class StorageException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class TaskIdNotFoundError(StorageException):
    pass


class RedisMixin:
    TASKS_KEY = "TASKS_ID"
    TASK_TTL = TTLTaskId

    def __init__(self):
        try:
            config = get_redis_ipc_settings()
            self.store = HashStore(RedisConnection(config))
        except RedisException as e:
            raise StorageException(e.detail)

    def set_field_for_task(self, task_id: Task_id, message):
        logger.info(f"Write {task_id} to {self.TASKS_KEY}")
        self.store.set(self.TASKS_KEY, {task_id: message})
        self.store.set_fttl(self.TASKS_KEY, task_id, self.TASK_TTL)
        fttl = self.store.fttl(task_id, task_id)
        logger.info(f"FTTL Task_id: {task_id} -> {fttl}")


class RedisTaskStorage(ITaskStorage, RedisMixin):
    def set(self, message: TaskMessage) -> bool:
        logger.info(f"Set Task_id: {message.task_id} -> {message.recognizer}")
        success = self.store.set(message.task_id, mapping=message.model_dump())

        self.store.set_key_ttl(message.task_id, self.TASK_TTL)
        ttl = self.store.ttl(message.task_id)
        logger.info(f"TTL Task_id: {message.task_id} -> {ttl}")

        return bool(success)

    def get(self, task_id: Task_id) -> TaskMessage | None:
        logger.info(f"Get Task_id: {task_id}")
        message = self.store.all(task_id)
        logger.debug(f"Response TaskMessage: {message}")
        if not message:
            raise TaskIdNotFoundError(f"Task_id: {task_id} not found")
        return TaskMessage.model_validate(message)

    def list(self) -> list[TaskMessage] | None:
        task_messages = []
        messages = self.store.all(self.TASKS_KEY)
        logger.debug(f"Response TaskMessage: {messages}")

        for task_id in messages.keys():
            message = self.store.all(task_id)
            if message:
                task_messages.append(TaskMessage.model_validate(message))
        return task_messages


class RedisRecognitionStorage(IRecognitionStorage, RedisMixin):
    def insert(self, task_status: TaskIdStatus) -> None:
        logger.info(f"Set Task_id: {task_status.task_id} -> {task_status.status}")
        self.set_field_for_task(task_status.task_id, task_status.model_dump_json())

    def select(self, task_id: Task_id) -> TaskIdStatus:
        logger.info(f"Get Task_id: {task_id}")
        message = self.store.all(self.TASKS_KEY, task_id)
        logger.debug(f"Response TaskMessage: {message}")
        if not message.values():
            raise TaskIdNotFoundError(f"Task_id: {task_id} not found")
        return TaskIdStatus.model_validate_json(tuple(message.values())[0])
