import json
import logging

from app.configs.settings import get_redis_ipc_settings
from app.drivers.ipc.redis_ipc import RedisIPC, RedisMessage
from app.interfaces.storages import ITaskStorage, Task_id, TaskMessage, TTLTaskId

logger = logging.getLogger("app.adapters.storages")


class Storage(Exception):
    pass


class TaskIdNotFoundError(Storage):
    def __init__(self, detail: str):
        self.detail = detail


class RedisTaskStorage(ITaskStorage):
    def __init__(self):
        self.redis = RedisIPC(get_redis_ipc_settings())
        assert self.redis.ping(), "Redis is not available"

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
