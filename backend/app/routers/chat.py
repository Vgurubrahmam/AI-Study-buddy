"""
Chat Router - /api/chat endpoints
Handles AI-powered question answering with RAG and Phi-3/Gemini fallback
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from datetime import datetime
from bson import ObjectId
from typing import Optional
import logging
import json

from app.models.chat import ChatMessage, ChatResponse, TokenUsage
from app.models.user import TokenData
from app.services.auth_service import get_current_user
from app.database import get_chat_history_collection, get_user_stats_collection
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Track ML availability
_ml_available = None
_gemini_available = None


def check_ml_available():
    """Check if ML dependencies (torch) are available"""
    global _ml_available
    if _ml_available is None:
        try:
            import torch
            _ml_available = True
        except ImportError:
            _ml_available = False
            logger.warning("PyTorch not installed - Phi-3 and RAG disabled, using Gemini only")
    return _ml_available


def get_phi3():
    """Lazy load Phi-3 client"""
    if not check_ml_available():
        raise ImportError("PyTorch required for Phi-3")
    from app.ml.phi3_client import get_phi3_client
    return get_phi3_client()


def get_rag():
    """Lazy load RAG service"""
    if not check_ml_available():
        return None
    from app.ml.rag_service import get_rag_service
    return get_rag_service()


def get_gemini():
    """Lazy load Gemini fallback client"""
    from app.ml.gemini_fallback import get_gemini_client
    return get_gemini_client()


@router.post("", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    current_user: Optional[TokenData] = Depends(get_current_user)
):
    """
    Send a message to the AI Study Buddy and get a response.
    
    - Uses RAG to augment responses with relevant study materials
    - Falls back to Gemini if Phi-3 is unavailable
    - Saves chat history if user is authenticated
    """
    logger.info(f"Chat request from user: {current_user.id if current_user else 'anonymous'}")
    
    try:
        # Get context from RAG if available (requires torch)
        context = ""
        rag = get_rag()
        if rag is not None:
            try:
                if rag.is_initialized() or True:  # Try to initialize
                    rag.initialize()
                    context = rag.get_context_for_query(message.message, n_results=3)
                    if context:
                        logger.info(f"Retrieved {len(context)} chars of context from RAG")
            except Exception as e:
                logger.warning(f"RAG retrieval failed: {e}")
        
        # Build system prompt with context
        system_prompt = """You are an intelligent AI Study Buddy, an educational assistant designed to help students learn effectively. You provide clear, accurate, and helpful explanations on various academic topics. Be encouraging, patient, and thorough in your responses. Use examples when helpful and break down complex concepts into understandable parts."""
        
        if context:
            system_prompt += f"\n\nUse the following context from study materials to help answer the question:\n\n{context}"
        
        # Try Phi-3 first (if torch is available)
        response_text = None
        token_usage = None
        model_used = None
        
        if check_ml_available():
            try:
                phi3 = get_phi3()
                response_text, token_usage = phi3.generate(
                    prompt=message.message,
                    system_prompt=system_prompt,
                    max_tokens=settings.max_tokens,
                    temperature=settings.temperature
                )
                model_used = "phi-3-mini-4k-instruct"
                logger.info("Response generated using Phi-3")
                
            except Exception as e:
                logger.warning(f"Phi-3 generation failed: {e}, trying Gemini fallback")
        
        # Use Gemini if Phi-3 not available or failed
        if response_text is None:
            try:
                gemini = get_gemini()
                if gemini.is_available():
                    response_text, token_usage = gemini.generate(
                        prompt=message.message,
                        system_prompt=system_prompt,
                        max_tokens=settings.max_tokens,
                        temperature=settings.temperature
                    )
                    model_used = "gemini-1.5-flash"
                    logger.info("Response generated using Gemini")
                else:
                    raise RuntimeError("No Gemini API keys configured")
                    
            except Exception as gemini_error:
                logger.error(f"Gemini generation failed: {gemini_error}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="AI service temporarily unavailable. Please configure Gemini API keys in .env"
                )
        
        # Save to chat history if user is authenticated
        if current_user and message.userId:
            try:
                chat_history = get_chat_history_collection()
                user_stats = get_user_stats_collection()
                
                # Save chat entry
                chat_doc = {
                    "userId": ObjectId(message.userId),
                    "userMessage": message.message,
                    "assistantResponse": response_text,
                    "createdAt": datetime.utcnow(),
                    "tokens": token_usage
                }
                await chat_history.insert_one(chat_doc)
                
                # Update user stats
                await user_stats.update_one(
                    {"userId": ObjectId(message.userId)},
                    {
                        "$inc": {"questionsAsked": 1},
                        "$set": {
                            "lastActiveDate": datetime.utcnow(),
                            "updatedAt": datetime.utcnow()
                        }
                    },
                    upsert=True
                )
                
                logger.info(f"Chat saved for user {message.userId}")
                
            except Exception as e:
                logger.error(f"Failed to save chat history: {e}")
                # Don't fail the request if history save fails
        
        return ChatResponse(
            response=response_text,
            tokens=TokenUsage(**token_usage) if token_usage else None,
            model=model_used
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}"
        )


@router.post("/stream")
async def chat_stream(
    message: ChatMessage,
    current_user: Optional[TokenData] = Depends(get_current_user)
):
    """
    Stream a response from the AI Study Buddy.
    
    - Returns server-sent events with response chunks
    - Useful for real-time typing effect in UI
    """
    
    async def generate():
        try:
            phi3 = get_phi3()
            
            system_prompt = """You are an intelligent AI Study Buddy, an educational assistant designed to help students learn effectively."""
            
            for chunk in phi3.generate_stream(
                prompt=message.message,
                system_prompt=system_prompt
            ):
                yield f"data: {json.dumps({'content': chunk, 'done': False})}\n\n"
            
            yield f"data: {json.dumps({'content': '', 'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {json.dumps({'error': str(e), 'done': True})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/model-info")
async def get_model_info():
    """
    Get information about the currently loaded AI model.
    """
    try:
        phi3 = get_phi3()
        info = phi3.get_model_info()
        
        # Add RAG info
        try:
            rag = get_rag()
            rag.initialize()
            info["rag"] = rag.get_stats()
        except:
            info["rag"] = {"status": "not initialized"}
        
        return info
        
    except Exception as e:
        return {
            "model_name": settings.model_name,
            "status": "not loaded",
            "error": str(e)
        }
