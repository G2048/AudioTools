import gradio as gr
from fastapi import FastAPI

from .pages.interfaces import Page


class WebUI:
    def __init__(self, page: Page):
        self.app = page.get_app()

    def run(self):
        self.app.queue()
        self.app.launch()

    def stop(self):
        self.app.close()

    def mount(self, app: FastAPI, path="/"):
        return gr.mount_gradio_app(app, self.app, path=path)
