from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import logging

from modules.llm.ollama_client import OllamaClient
from modules.llm.prompt_builder import build_chat_prompt
from modules.llm.guardrails import is_safe_query
from modules.rag.retriever import RAGRetriever
import config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.websocket("/chat/{session_id}")
async def chat_websocket(websocket: WebSocket, session_id: str):
    await websocket.accept()
    logger.info(f"Chat WebSocket connected: {session_id}")

    # Import here to avoid circular imports
    from routers.assess import get_session
    session = get_session(session_id)

    if not session:
        await websocket.send_text(json.dumps({
            "type": "error",
            "content": "Session not found. Please complete an assessment first."
        }))
        await websocket.close()
        return

    conversation_history = session.get("conversation_history", [])
    ollama = OllamaClient()

    # Initialize RAG for dynamic retrieval
    rag = None
    try:
        rag = RAGRetriever(config.CHROMA_DB_PATH)
    except Exception as e:
        logger.warning(f"RAG not available in chat: {e}")

    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "").strip()

            if not user_message:
                continue

            # Safety check
            if not is_safe_query(user_message):
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": "I can only assist with health-related questions. Please ask about symptoms, conditions, or general wellness."
                }))
                continue

            # Re-retrieve RAG context for this specific question
            rag_context = session.get("rag_context", "")
            if rag:
                try:
                    new_docs = rag.retrieve(user_message, top_k=3)
                    if new_docs:
                        rag_context = "\n\n".join([d["text"] for d in new_docs])
                except Exception as e:
                    logger.warning(f"RAG retrieval in chat failed: {e}")

            conversation_history.append({"role": "user", "content": user_message})

            # Build prompt with full context
            prompt = build_chat_prompt(
                user_message=user_message,
                conversation_history=conversation_history,
                session_context=session,
                rag_context=rag_context,
            )

            # Stream LLM response token by token
            full_response = ""
            await websocket.send_text(json.dumps({"type": "start"}))

            try:
                async for token in ollama.stream(prompt):
                    full_response += token
                    await websocket.send_text(json.dumps({
                        "type": "token",
                        "content": token
                    }))
            except Exception as e:
                logger.error(f"LLM streaming failed: {e}")
                full_response = "I'm having trouble generating a response right now. Please try again."
                await websocket.send_text(json.dumps({
                    "type": "token",
                    "content": full_response
                }))

            await websocket.send_text(json.dumps({"type": "end"}))

            conversation_history.append({"role": "assistant", "content": full_response})
            session["conversation_history"] = conversation_history

    except WebSocketDisconnect:
        logger.info(f"Chat WebSocket disconnected: {session_id}")
    except Exception as e:
        logger.error(f"Chat error: {e}")
        try:
            await websocket.send_text(json.dumps({"type": "error", "content": str(e)}))
        except Exception:
            pass
