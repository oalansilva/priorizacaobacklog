import abc
import sqlite3
import json
import os
from typing import List, Optional
from app.models.db import BacklogItem, Conversation, ConversationMessage, SystemSettings, Roadmap, RoadmapItem, User

class DatabaseRepository(abc.ABC):
    @abc.abstractmethod
    def add_item(self, item: BacklogItem) -> BacklogItem:
        pass

    @abc.abstractmethod
    def list_items(self, user_id: Optional[str] = None) -> List[BacklogItem]:
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
    
    @abc.abstractmethod
    def save_roadmap(self, roadmap: Roadmap) -> Roadmap:
        pass
    
    @abc.abstractmethod
    def list_roadmaps(self, user_id: Optional[str] = None) -> List[Roadmap]:
        pass
    
    @abc.abstractmethod
    def get_roadmap(self, roadmap_id: str) -> Optional[Roadmap]:
        pass
    
    @abc.abstractmethod
    def delete_roadmap(self, roadmap_id: str) -> bool:
        pass
        
    @abc.abstractmethod
    def create_user(self, user: User) -> User:
        """Cria um novo usuário."""
        pass
        
    @abc.abstractmethod
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Busca usuário por email."""
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
            
            # Create roadmaps table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS roadmaps (
                    id TEXT PRIMARY KEY,
                    created_at TEXT,
                    capacidade_total INTEGER,
                    percentual_sustentacao INTEGER,
                    capacidade_iniciativas INTEGER,
                    total_itens INTEGER,
                    itens_priorizados INTEGER,
                    itens_despriorizados INTEGER,
                    horas_alocadas INTEGER,
                    peso_financeiro INTEGER,
                    peso_negocios INTEGER,
                    peso_cliente INTEGER,
                    peso_okr INTEGER,
                    itens_json TEXT
                )
                )
            """)

            # Create users table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    full_name TEXT,
                    created_at TEXT
                )
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

        return item

    def list_items(self, user_id: Optional[str] = None) -> List[BacklogItem]:
        items = []
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute("SELECT * FROM items WHERE user_id = ? ORDER BY prioridade ASC, created_at ASC", (user_id,))
            else:
                # Fallback for legacy or admin (or show all if no user_id passed)
                # Ideally in multi-user mode we might want to strictly require user_id
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

    def save_roadmap(self, roadmap: Roadmap) -> Roadmap:
        with sqlite3.connect(self.db_path) as conn:
            # Serializar itens para JSON
            itens_json = json.dumps([item.model_dump() for item in roadmap.itens])
            
            conn.execute(
                """INSERT INTO roadmaps 
                   (id, created_at, capacidade_total, percentual_sustentacao, capacidade_iniciativas,
                    total_itens, itens_priorizados, itens_despriorizados, horas_alocadas,
                    peso_financeiro, peso_negocios, peso_cliente, peso_okr, itens_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    roadmap.id, roadmap.created_at, roadmap.capacidade_total,
                    roadmap.percentual_sustentacao, roadmap.capacidade_iniciativas,
                    roadmap.total_itens, roadmap.itens_priorizados, roadmap.itens_despriorizados,
                    roadmap.horas_alocadas, roadmap.peso_financeiro, roadmap.peso_negocios,
                    roadmap.peso_cliente, roadmap.peso_okr, itens_json
                )
            )
        return roadmap

        return roadmap

    def list_roadmaps(self, user_id: Optional[str] = None) -> List[Roadmap]:
        roadmaps = []
        with sqlite3.connect(self.db_path) as conn:
            if user_id:
                cursor = conn.execute(
                    "SELECT * FROM roadmaps WHERE user_id = ? ORDER BY created_at DESC", 
                    (user_id,)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM roadmaps ORDER BY created_at DESC"
                )
                
            for row in cursor:
                itens_data = json.loads(row[13])  # itens_json é a coluna 13
                itens = [RoadmapItem(**item) for item in itens_data]
                
                roadmaps.append(Roadmap(
                    id=row[0],
                    created_at=row[1],
                    capacidade_total=row[2],
                    percentual_sustentacao=row[3],
                    capacidade_iniciativas=row[4],
                    total_itens=row[5],
                    itens_priorizados=row[6],
                    itens_despriorizados=row[7],
                    horas_alocadas=row[8],
                    peso_financeiro=row[9],
                    peso_negocios=row[10],
                    peso_cliente=row[11],
                    peso_okr=row[12],
                    itens=itens
                ))
        return roadmaps

    def get_roadmap(self, roadmap_id: str) -> Optional[Roadmap]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT * FROM roadmaps WHERE id = ?", (roadmap_id,)
            )
            row = cursor.fetchone()
            if row:
                itens_data = json.loads(row[13])
                itens = [RoadmapItem(**item) for item in itens_data]
                
                return Roadmap(
                    id=row[0],
                    created_at=row[1],
                    capacidade_total=row[2],
                    percentual_sustentacao=row[3],
                    capacidade_iniciativas=row[4],
                    total_itens=row[5],
                    itens_priorizados=row[6],
                    itens_despriorizados=row[7],
                    horas_alocadas=row[8],
                    peso_financeiro=row[9],
                    peso_negocios=row[10],
                    peso_cliente=row[11],
                    peso_okr=row[12],
                    itens=itens
                )
        return None

    def delete_roadmap(self, roadmap_id: str) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("DELETE FROM roadmaps WHERE id = ?", (roadmap_id,))
            return cursor.rowcount > 0

    def create_user(self, user: User) -> User:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO users (id, email, password_hash, full_name, created_at) VALUES (?, ?, ?, ?, ?)",
                (user.id, user.email, user.password_hash, user.full_name, user.created_at)
            )
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT * FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            if row:
                return User(
                    id=row[0],
                    email=row[1],
                    password_hash=row[2],
                    full_name=row[3],
                    created_at=row[4]
                )
        return None


class DynamoDBRepository(DatabaseRepository):
    def __init__(self):
        import boto3
        from app.config import get_settings
        
        self.settings = get_settings()
        self.dynamodb = boto3.resource('dynamodb', region_name=self.settings.aws_region)
        self.table_items = self.dynamodb.Table(self.settings.dynamodb_table_items)
        self.table_conversations = self.dynamodb.Table(self.settings.dynamodb_table_conversations)
        self.table_settings = self.dynamodb.Table(self.settings.dynamodb_table_settings)
        self.table_settings = self.dynamodb.Table(self.settings.dynamodb_table_settings)
        self.table_roadmaps = self.dynamodb.Table(self.settings.dynamodb_table_roadmaps)
        self.table_users = self.dynamodb.Table(self.settings.dynamodb_table_users)

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

    def list_items(self, user_id: Optional[str] = None) -> List[BacklogItem]:
        # Scan is okay for small backlogs, but for production with millions of items 
        # Query with GSI would be better. For now, Scan is sufficient.
        
        from boto3.dynamodb.conditions import Key, Attr
        
        scan_kwargs = {}
        if user_id:
            scan_kwargs['FilterExpression'] = Attr('user_id').eq(user_id)
            
        response = self.table_items.scan(**scan_kwargs)
        items_data = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = self.table_items.scan(**scan_kwargs)
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
        # Settings table has String key "1", but model uses int 1.
        response = self.table_settings.get_item(Key={'id': str(1)})
        item = response.get('Item')
        if item:
            # DynamoDB stores numbers as Decimal, Pydantic handles conversion
            # Ensure ID is passed as int to model if model expects int
            if 'id' in item:
                item['id'] = int(item['id'])
            return SystemSettings(**item)
        
        # If not found, create default
        default_settings = SystemSettings(id=1)
        self.update_settings(default_settings)
        return default_settings

    def update_settings(self, settings: SystemSettings) -> SystemSettings:
        data = settings.model_dump()
        data = self._convert_floats_to_decimals(data)
        # Force ID to be string for DynamoDB
        data['id'] = str(data['id'])
        self.table_settings.put_item(Item=data)
        return settings
    
    def save_roadmap(self, roadmap: Roadmap) -> Roadmap:
        data = roadmap.model_dump()
        data = self._convert_floats_to_decimals(data)
        self.table_roadmaps.put_item(Item=data)
        return roadmap
    
    def list_roadmaps(self, user_id: Optional[str] = None) -> List[Roadmap]:
        from boto3.dynamodb.conditions import Key, Attr
        
        scan_kwargs = {}
        if user_id:
            scan_kwargs['FilterExpression'] = Attr('user_id').eq(user_id)
            
        response = self.table_roadmaps.scan(**scan_kwargs)
        roadmaps_data = response.get('Items', [])
        
        while 'LastEvaluatedKey' in response:
            scan_kwargs['ExclusiveStartKey'] = response['LastEvaluatedKey']
            response = self.table_roadmaps.scan(**scan_kwargs)
            roadmaps_data.extend(response.get('Items', []))
        
        roadmaps = [Roadmap(**roadmap) for roadmap in roadmaps_data]
        roadmaps.sort(key=lambda x: x.created_at, reverse=True)
        return roadmaps
    
    def get_roadmap(self, roadmap_id: str) -> Optional[Roadmap]:
        response = self.table_roadmaps.get_item(Key={'id': roadmap_id})
        item = response.get('Item')
        if item:
            return Roadmap(**item)
        return None
    
    def delete_roadmap(self, roadmap_id: str) -> bool:
        try:
            self.table_roadmaps.delete_item(Key={'id': roadmap_id})
            return True
        except Exception:
            return False
            
    def create_user(self, user: User) -> User:
        data = user.model_dump()
        # DynamoDB doesn't like float, but User doesn't have floats.
        self.table_users.put_item(Item=data)
        return user

    def get_user_by_email(self, email: str) -> Optional[User]:
        # Scan is inefficient for getting by email if not key. 
        # Ideally Email should be the Key or GSI. Assuming SCAN for now or if ID is not email.
        # Ideally we should redesign table to use Email as PK or have GSI.
        # But for this MVP/Refactor, a Scan with Filter or GSI is needed.
        # Let's assume Scan with FilterExpression for now as it's simplest without changing infra definition too much right now.
        from boto3.dynamodb.conditions import Key, Attr
        
        response = self.table_users.scan(
            FilterExpression=Attr('email').eq(email)
        )
        items = response.get('Items', [])
        if items:
            return User(**items[0])
            
        return None


def get_repository() -> DatabaseRepository:
    from app.config import get_settings
    settings = get_settings()
    
    if settings.database_type.lower() == "dynamodb":
        return DynamoDBRepository()
    
    return SQLiteRepository()

