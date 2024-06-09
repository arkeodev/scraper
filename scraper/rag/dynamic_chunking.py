import json


def determine_chunk_size(data: str) -> int:
    return max(100, len(data) // 20)


def chunk_data(data: str) -> list:
    size = determine_chunk_size(data)
    return [data[i : i + size] for i in range(0, len(data), size)]


def data_to_json(data: list) -> str:
    return json.dumps({"chunks": data})
