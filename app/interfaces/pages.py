from abc import ABC, abstractmethod

import gradio as gr


class Page(ABC):
    @abstractmethod
    def get_app() -> gr.Blocks:
        pass

    @property
    @abstractmethod
    def title(self) -> str:
        pass


class Action(ABC):
    @abstractmethod
    def execute(self, *args: tuple, **kwargs: dict):
        pass
