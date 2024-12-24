import uvicorn

import webui

from fastapi import FastAPI


app = FastAPI()
app = webui.set_app(app)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
