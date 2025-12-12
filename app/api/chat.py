from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from app.core.database import get_repository, DatabaseRepository
from app.models.db import Conversation, ConversationMessage
from app.core.agent import get_agent_executor
from app.security import get_current_user, TokenData
from app.user_context import user_id_ctx


router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

from fastapi.responses import StreamingResponse
import json
import asyncio
import logging
import traceback

logger = logging.getLogger(__name__)

@router.post("", response_model=None)
async def chat(
    request: ChatRequest, 
    repo: DatabaseRepository = Depends(get_repository),
    current_user: TokenData = Depends(get_current_user)
):
    logger.debug(f"Chat endpoint called for conversation {request.conversation_id} by user {current_user.user_id}")
    
    # Set context for this request
    token = user_id_ctx.set(current_user.user_id)
    # 1. Retrieve or create conversation
    if request.conversation_id:
        conversation = repo.get_conversation(request.conversation_id)
        if not conversation:
            conversation = Conversation(id=request.conversation_id)
    else:
        conversation = Conversation()

    # 2. Add user message to DB model
    conversation.messages.append(ConversationMessage(role="user", content=request.message))
    
    # 3. Prepare messages for LangGraph
    langchain_messages = []
    for msg in conversation.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        elif msg.role == "assistant":
            langchain_messages.append(AIMessage(content=msg.content))
    
    # 4. Process with Agent (LangGraph)
    agent_graph = get_agent_executor(repo)

    async def event_generator():
        full_response = ""
        
        try:
            # Stream events from the graph
            event_count = 0
            async for event in agent_graph.astream_events(
                {"messages": langchain_messages}, 
                version="v1"
            ):
                kind = event.get("event")
                
                # Stream LLM tokens
                if kind == "on_chat_model_stream":
                    try:
                        chunk = event.get("data", {}).get("chunk")
                        if chunk and hasattr(chunk, "content"):
                            content = chunk.content
                            
                            # Handle list content (common in complex models/tool use)
                            if isinstance(content, list):
                                text_content = ""
                                for block in content:
                                    if isinstance(block, str):
                                        text_content += block
                                    elif isinstance(block, dict) and "text" in block:
                                        text_content += block["text"]
                                content = text_content
                            
                            if content and isinstance(content, str):
                                full_response += content
                                event_count += 1
                                yield content
                    except Exception as chunk_error:
                        logger.error(f"Error processing chunk: {chunk_error}")
                        continue
            
            logger.debug(f"Stream finished. Total events: {event_count}. Response length: {len(full_response)}")

            # 5. Add agent response to DB model (after streaming completes)
            if full_response:
                logger.debug(f"Stream complete, saving conversation {conversation.id}")
                conversation.messages.append(ConversationMessage(role="assistant", content=full_response))
                repo.save_conversation(conversation)
            else:
                logger.warning(f"No response generated for conversation {conversation.id}. Event count: {event_count}")
                yield "\n\n[Aviso: O modelo não gerou nenhuma resposta. Verifique os logs.]"
                
        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(f"Error in event_generator: {e}\n{error_trace}")
            yield f"\n\n[Erro ao processar: {str(e)}]"

    async def cleanup_generator():
        try:
            async for chunk in event_generator():
                yield chunk
        finally:
            # Reset context after generator finishes
            user_id_ctx.reset(token)

    return StreamingResponse(cleanup_generator(), media_type="text/plain", headers={"X-Conversation-ID": conversation.id})
