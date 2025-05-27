import json
import logging

from app.configs.settings import get_redis_ipc_settings
from app.drivers.ipc.redis_ipc import RedisException, RedisIPC, RedisMessage
from app.interfaces.storages import ITaskStorage, Task_id, TaskMessage, TTLTaskId

logger = logging.getLogger("app.adapters.storages")


class StorageException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class TaskIdNotFoundError(StorageException):
    pass


class RedisTaskStorage(ITaskStorage):
    def __init__(self):
        try:
            self.redis = RedisIPC(get_redis_ipc_settings())
            self.redis.ping()
        except RedisException as e:
            raise StorageException(e.detail)

    def set(self, message: TaskMessage) -> bool:
        logger.info(f"Set Task_id: {message.task_id} -> {message.recognizer}")
        return self.redis.setx(
            RedisMessage(
                key=message.task_id, value=message.model_dump_json(), ttl=TTLTaskId
            )
        )

    def get(self, task_id: Task_id) -> TaskMessage | None:
        logger.info(f"Get Task_id: {task_id}")
        message = self.redis.get(task_id)
        if message.value is None:
            raise TaskIdNotFoundError(f"Task with id {task_id} not found")
        else:
            value = json.loads(message.value)
            logger.debug(f"Response TaskMessage: {value}")
        return TaskMessage(task_id=message.key, **value)
