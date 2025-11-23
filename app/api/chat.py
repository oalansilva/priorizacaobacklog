from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from langchain_core.messages import HumanMessage, AIMessage
from app.core.database import get_repository, DatabaseRepository
from app.models.db import Conversation, ConversationMessage
from app.core.agent import get_agent_executor

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, repo: DatabaseRepository = Depends(get_repository)):
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
    
    # LangGraph expects {"messages": [...]}
    result = await agent_graph.ainvoke({"messages": langchain_messages})
    
    # Result["messages"] contains the full history including new messages
    # We want the last message which should be from the assistant
    last_message = result["messages"][-1]
    agent_response_text = last_message.content

    # 5. Add agent response to DB model
    conversation.messages.append(ConversationMessage(role="assistant", content=agent_response_text))
    
    # 6. Save conversation
    repo.save_conversation(conversation)

    return ChatResponse(response=agent_response_text, conversation_id=conversation.id)
