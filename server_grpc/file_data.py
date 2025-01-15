import datetime

FILES: dict[str, dict[str, str | int | bytes]] = {
    "123e4567-e89b-12d3-a456-426614174000": {
        "name": "example.txt",
        "size": 1024,
        "create_datetime": datetime.datetime.now().isoformat(),
        "mimetype": "text/plain",
        "content": b"Hello, this is an example file content.",
    }
}
