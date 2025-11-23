import abc
import sqlite3
import json
import os
from typing import List, Optional
from app.models.db import BacklogItem, Conversation, ConversationMessage

class DatabaseRepository(abc.ABC):
    @abc.abstractmethod
    def add_item(self, item: BacklogItem) -> BacklogItem:
        pass

    @abc.abstractmethod
    def list_items(self) -> List[BacklogItem]:
        pass

    @abc.abstractmethod
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        pass

    @abc.abstractmethod
    def save_conversation(self, conversation: Conversation) -> Conversation:
        pass

    @abc.abstractmethod
    def update_item(self, item: BacklogItem) -> BacklogItem:
        pass

    @abc.abstractmethod
    def clear_items(self) -> None:
        pass

class SQLiteRepository(DatabaseRepository):
    def __init__(self, db_path: str = "backlog.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id TEXT PRIMARY KEY,
                    titulo TEXT,
                    descricao TEXT,
                    valor_negocio TEXT,
                    esforco_estimado INTEGER,
                    area TEXT,
                    dependencias TEXT,
                    prazo TEXT,
                    status TEXT,
                    created_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    messages TEXT,
                    updated_at TEXT
                )
            """)

    def add_item(self, item: BacklogItem) -> BacklogItem:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.id, item.titulo, item.descricao, item.valor_negocio,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.prazo, item.status, item.created_at
                )
            )
        return item

    def list_items(self) -> List[BacklogItem]:
        items = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM items")
            for row in cursor:
                items.append(BacklogItem(
                    id=row[0], titulo=row[1], descricao=row[2], valor_negocio=row[3],
                    esforco_estimado=row[4], area=row[5], dependencias=row[6],
                    prazo=row[7], status=row[8], created_at=row[9]
                ))
        return items

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT messages, updated_at FROM conversations WHERE id = ?", (conversation_id,))
            row = cursor.fetchone()
            if row:
                messages_data = json.loads(row[0])
                messages = [ConversationMessage(**msg) for msg in messages_data]
                return Conversation(id=conversation_id, messages=messages, updated_at=row[1])
        return None

    def save_conversation(self, conversation: Conversation) -> Conversation:
        messages_json = json.dumps([msg.model_dump() for msg in conversation.messages])
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR REPLACE INTO conversations (id, messages, updated_at) VALUES (?, ?, ?)",
                (conversation.id, messages_json, conversation.updated_at)
            )
        return conversation

    def update_item(self, item: BacklogItem) -> BacklogItem:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE items SET titulo=?, descricao=?, valor_negocio=?, esforco_estimado=?, area=?, dependencias=?, prazo=?, status=? WHERE id=?",
                (
                    item.titulo, item.descricao, item.valor_negocio,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.prazo, item.status, item.id
                )
            )
        return item

    def clear_items(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM items")

# TODO: Implement DynamoDBRepository when ready for production
def get_repository() -> DatabaseRepository:
    # Simple factory for now, can be expanded based on env vars
    return SQLiteRepository()
