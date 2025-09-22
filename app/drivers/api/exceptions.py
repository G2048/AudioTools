class ClientHTTPException(Exception):
    def __init__(self, status_code: str | int, detail: dict | None = None):
        self.status_code = status_code
        self.detail = detail
        super().__init__(status_code, detail)

    def __str__(self):
        return f"{self.status_code}: {self.detail}"
