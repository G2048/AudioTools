import gradio as gr
from fastapi import FastAPI

from app.interfaces import Page


class WebUI:
    def __init__(self, page: Page):
        self.app = page.get_app()

    @classmethod
    def pages(cls, app: FastAPI, pages: list[Page], path: str = "/") -> FastAPI:
        list_apps = []
        list_titles = []
        for page in pages:
            list_apps.append(cls(page).app)
            list_titles.append(page.title)

        apps = gr.TabbedInterface(
            list_apps,
            list_titles,
            title="Audio Diffusion",
            css="footer {visibility: hidden}",
        )
        return gr.mount_gradio_app(app, apps, path=path)

    def run(self):
        self.app.queue()
        self.app.launch()

    def stop(self):
        self.app.close()

    def mount(self, app: FastAPI, path="/") -> FastAPI:
        return gr.mount_gradio_app(app, self.app, path=path)
