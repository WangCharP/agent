import json
class StreamFormatter:
    @staticmethod
    def format(type_: str, data: any) -> str:
        return json.dumps({"type": type_, "data": data}, ensure_ascii=False) + "\n"