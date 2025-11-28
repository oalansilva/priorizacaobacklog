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
                    must_have TEXT DEFAULT 'Não',
                    estimado_qp TEXT DEFAULT 'Não',
                    justificativa TEXT
                )
            """)
            
            # Migration: Add justificativa column if not exists (for existing DBs)
            try:
                conn.execute("ALTER TABLE items ADD COLUMN justificativa TEXT")
            except sqlite3.OperationalError:
                pass
            
            # Migration: Add prioridade column if not exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN prioridade INTEGER DEFAULT 999")
            except sqlite3.OperationalError:
                pass
            
            # Migration: Add must_have column if not exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN must_have TEXT DEFAULT 'Não'")
            except sqlite3.OperationalError:
                pass

            # Migration: Add score column if not exists
            try:
                conn.execute("ALTER TABLE items ADD COLUMN score REAL DEFAULT 0.0")
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
                "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    item.id, item.titulo, item.descricao,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.status, item.prioridade, item.created_at,
                    item.categoria, item.impacto_financeiro, item.impacto_negocios,
                    item.impacto_cliente, item.okr, item.must_have, item.estimado_qp, item.justificativa,
                    item.score
                )
            )
        return item

    def list_items(self) -> List[BacklogItem]:
        items = []
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM items ORDER BY prioridade ASC, created_at ASC")
            for row in cursor:
                # Handle potential missing columns if DB schema varies (though migration should fix it)
                # Assuming schema matches add_item order
                items.append(BacklogItem(
                    id=row[0], titulo=row[1], descricao=row[2],
                    esforco_estimado=row[3], area=row[4], dependencias=row[5],
                    status=row[6], prioridade=row[7], created_at=row[8],
                    categoria=row[9], impacto_financeiro=row[10], impacto_negocios=row[11],
                    impacto_cliente=row[12], okr=row[13], must_have=row[14], estimado_qp=row[15], justificativa=row[16],
                    score=row[17] if len(row) > 17 else 0.0
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
                   area=?, dependencias=?, status=?, prioridade=?, categoria=?, impacto_financeiro=?, 
                   impacto_negocios=?, impacto_cliente=?, okr=?, must_have=?, estimado_qp=?, justificativa=?, score=? WHERE id=?""",
                (
                    item.titulo, item.descricao,
                    item.esforco_estimado, item.area, item.dependencias,
                    item.status, item.prioridade, item.categoria, item.impacto_financeiro,
                    item.impacto_negocios, item.impacto_cliente, item.okr, item.must_have, item.estimado_qp,
                    item.justificativa, item.score,
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


class DynamoDBRepository(DatabaseRepository):
    def __init__(self):
        import boto3
        from app.config import get_settings
        
        self.settings = get_settings()
        self.dynamodb = boto3.resource('dynamodb', region_name=self.settings.aws_region)
        self.table_items = self.dynamodb.Table(self.settings.dynamodb_table_items)
        self.table_conversations = self.dynamodb.Table(self.settings.dynamodb_table_conversations)
        self.table_settings = self.dynamodb.Table(self.settings.dynamodb_table_settings)

    def _convert_floats_to_decimals(self, obj):
        from decimal import Decimal
        if isinstance(obj, float):
            return Decimal(str(obj))
        elif isinstance(obj, dict):
            return {k: self._convert_floats_to_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_floats_to_decimals(v) for v in obj]
        return obj

    def add_item(self, item: BacklogItem) -> BacklogItem:
        # Convert float/int to Decimal is handled by boto3 for standard types, 
        # but we need to ensure dict format is clean
        item_dict = item.model_dump()
        item_dict = self._convert_floats_to_decimals(item_dict)
        self.table_items.put_item(Item=item_dict)
        return item

    def list_items(self) -> List[BacklogItem]:
        # Scan is okay for small backlogs, but for production with millions of items 
        # Query with GSI would be better. For now, Scan is sufficient.
        response = self.table_items.scan()
        items_data = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = self.table_items.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items_data.extend(response.get('Items', []))
            
        # Convert decimals to int/float if needed (boto3 returns Decimal)
        # Pydantic handles type conversion automatically
        items = [BacklogItem(**item) for item in items_data]
        
        # Sort in memory (DynamoDB scan doesn't sort)
        # Sort by priority (asc) then created_at (asc)
        items.sort(key=lambda x: (x.prioridade, x.created_at))
        return items

    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        response = self.table_conversations.get_item(Key={'id': conversation_id})
        item = response.get('Item')
        if item:
            return Conversation(**item)
        return None

    def save_conversation(self, conversation: Conversation) -> Conversation:
        data = conversation.model_dump()
        data = self._convert_floats_to_decimals(data)
        self.table_conversations.put_item(Item=data)
        return conversation

    def update_item(self, item: BacklogItem) -> BacklogItem:
        item_dict = item.model_dump()
        item_dict = self._convert_floats_to_decimals(item_dict)
        self.table_items.put_item(Item=item_dict)
        return item

    def clear_items(self) -> None:
        # Scan and delete (inefficient but works for small datasets)
        # For production, dropping and recreating table is faster
        scan = self.table_items.scan()
        with self.table_items.batch_writer() as batch:
            for each in scan['Items']:
                batch.delete_item(Key={'id': each['id']})

    def delete_item(self, item_id: str) -> bool:
        try:
            self.table_items.delete_item(Key={'id': item_id})
            return True
        except Exception:
            return False

    def get_settings(self) -> SystemSettings:
        response = self.table_settings.get_item(Key={'id': 1})
        item = response.get('Item')
        if item:
            # DynamoDB stores numbers as Decimal, Pydantic handles conversion
            return SystemSettings(**item)
        
        # If not found, create default
        default_settings = SystemSettings(id=1)
        self.update_settings(default_settings)
        return default_settings

    def update_settings(self, settings: SystemSettings) -> SystemSettings:
        data = settings.model_dump()
        data = self._convert_floats_to_decimals(data)
        self.table_settings.put_item(Item=data)
        return settings


def get_repository() -> DatabaseRepository:
    from app.config import get_settings
    settings = get_settings()
    
    if settings.database_type.lower() == "dynamodb":
        return DynamoDBRepository()
    
    return SQLiteRepository()

