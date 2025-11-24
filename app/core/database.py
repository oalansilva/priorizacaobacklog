import abc
import sqlite3
import json
import os
from typing import List, Optional
from app.models.db import BacklogItem, Conversation, ConversationMessage, SystemSettings

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

    @abc.abstractmethod
    def delete_item(self, item_id: str) -> bool:
        pass

    @abc.abstractmethod
    def get_settings(self) -> SystemSettings:
        pass

    @abc.abstractmethod
    def update_settings(self, settings: SystemSettings) -> SystemSettings:
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
                    estimado_qp TEXT DEFAULT 'Não',
                    justificativa TEXT
                )
            """)
            
            # Migration: Add justificativa column if not exists (for existing DBs)
            try:
                conn.execute("ALTER TABLE items ADD COLUMN justificativa TEXT")
            except sqlite3.OperationalError:
                pass

            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    messages TEXT,
                    updated_at TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    capacidade_total INTEGER,
                    percentual_sustentacao INTEGER,
                    peso_financeiro INTEGER DEFAULT 25,
                    peso_negocios INTEGER DEFAULT 25,
                    peso_cliente INTEGER DEFAULT 25,
                    peso_okr INTEGER DEFAULT 25,
                    updated_at TEXT
                )
            """)
            
            # Migration: Add weight columns if not exists
            for col in ['peso_financeiro', 'peso_negocios', 'peso_cliente', 'peso_okr']:
                try:
                    conn.execute(f"ALTER TABLE settings ADD COLUMN {col} INTEGER DEFAULT 25")
                except sqlite3.OperationalError:
                    pass

            # Insert default settings if not exists
            conn.execute("""
                INSERT OR IGNORE INTO settings (id, capacidade_total, percentual_sustentacao, 
                   peso_financeiro, peso_negocios, peso_cliente, peso_okr, updated_at) 
                   VALUES (1, 1000, 20, 25, 25, 25, 25, datetime('now'))
            """)

    def add_item(self, item: BacklogItem) -> BacklogItem:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.id, item.titulo, item.descricao,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.status, item.created_at,
                    item.categoria, item.impacto_financeiro, item.impacto_negocios,
                    item.impacto_cliente, item.okr, item.estimado_qp, item.justificativa
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
                    estimado_qp=row[13] if len(row) > 13 else "Não",
                    justificativa=row[14] if len(row) > 14 else None
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
                   impacto_negocios=?, impacto_cliente=?, okr=?, estimado_qp=?, justificativa=? WHERE id=?""",
                (
                    item.titulo, item.descricao,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.status, item.categoria, item.impacto_financeiro,
                    item.impacto_negocios, item.impacto_cliente, item.okr, item.estimado_qp,
                    item.justificativa,
                    item.id
                )
            )
        return item

    def clear_items(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM items")

    def delete_item(self, item_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
            return cursor.rowcount > 0

    def get_settings(self) -> SystemSettings:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT capacidade_total, percentual_sustentacao, 
                       peso_financeiro, peso_negocios, peso_cliente, peso_okr,
                       updated_at 
                FROM settings WHERE id = 1
            """)
            row = cursor.fetchone()
            if row:
                return SystemSettings(
                    capacidade_total=row[0],
                    percentual_sustentacao=row[1],
                    peso_financeiro=row[2] if row[2] is not None else 25,
                    peso_negocios=row[3] if row[3] is not None else 25,
                    peso_cliente=row[4] if row[4] is not None else 25,
                    peso_okr=row[5] if row[5] is not None else 25,
                    updated_at=row[6]
                )
            return SystemSettings()

    def update_settings(self, settings: SystemSettings) -> SystemSettings:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """UPDATE settings SET 
                   capacidade_total=?, percentual_sustentacao=?, 
                   peso_financeiro=?, peso_negocios=?, peso_cliente=?, peso_okr=?,
                   updated_at=? WHERE id=1""",
                (
                    settings.capacidade_total, settings.percentual_sustentacao,
                    settings.peso_financeiro, settings.peso_negocios, settings.peso_cliente, 
                    settings.peso_okr,
                    settings.updated_at
                )
            )
        return settings

# TODO: Implement DynamoDBRepository when ready for production
def get_repository() -> DatabaseRepository:
    # Simple factory for now, can be expanded based on env vars
    return SQLiteRepository()
