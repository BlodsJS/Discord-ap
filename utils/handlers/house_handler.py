# utils/handlers/test_handler.py
import json
from pathlib import Path

DB_FILE = Path("utils/dbs/tests.json")

class TestHandler:
    @staticmethod
    def load_data():
        if not DB_FILE.exists():
            return {}
        return json.loads(DB_FILE.read_text(encoding="utf-8"))

    @staticmethod
    def save_data(data: dict):
        DB_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")
    @staticmethod
    def clear_user(user_id: int):
        data = TestHandler.load_data()
        data.pop(str(user_id), None)
        TestHandler.save_data(data)

    @staticmethod
    async def register_answer(thread_id: int, user_id: int, question: str, answer: str):
        data = TestHandler.load_data()

        if str(user_id) not in data:
            data[str(user_id)] = {}

        if str(thread_id) not in data[str(user_id)]:
            data[str(user_id)][str(thread_id)] = {}

        data[str(user_id)][str(thread_id)][question] = answer
        TestHandler.save_data(data)