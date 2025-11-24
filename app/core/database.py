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
                    esforco_estimado INTEGER,
                    area TEXT,
                    dependencias TEXT,
                    status TEXT,
                    created_at TEXT,
                    categoria TEXT,
                    impacto_financeiro TEXT DEFAULT 'Não',
                    impacto_negocios TEXT DEFAULT 'Não',
                    impacto_cliente TEXT DEFAULT 'Não',
                    okr TEXT DEFAULT 'Não',
                    estimado_qp TEXT DEFAULT 'Não'
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
                "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.id, item.titulo, item.descricao,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.status, item.created_at,
                    item.categoria, item.impacto_financeiro, item.impacto_negocios,
                    item.impacto_cliente, item.okr, item.estimado_qp
                )
            )
        return item

    def list_items(self) -> List[BacklogItem]:
        items = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM items")
            for row in cursor:
                items.append(BacklogItem(
                    id=row[0], titulo=row[1], descricao=row[2],
                    esforco_estimado=row[3], area=row[4], dependencias=row[5],
                    status=row[6], created_at=row[7],
                    categoria=row[8] if len(row) > 8 else None,
                    impacto_financeiro=row[9] if len(row) > 9 else "Não",
                    impacto_negocios=row[10] if len(row) > 10 else "Não",
                    impacto_cliente=row[11] if len(row) > 11 else "Não",
                    okr=row[12] if len(row) > 12 else "Não",
                    estimado_qp=row[13] if len(row) > 13 else "Não"
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
                """UPDATE items SET titulo=?, descricao=?, esforco_estimado=?, 
                   area=?, dependencias=?, status=?, categoria=?, impacto_financeiro=?, 
                   impacto_negocios=?, impacto_cliente=?, okr=?, estimado_qp=? WHERE id=?""",
                (
                    item.titulo, item.descricao,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.status, item.categoria, item.impacto_financeiro,
                    item.impacto_negocios, item.impacto_cliente, item.okr, item.estimado_qp,
                    item.id
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
