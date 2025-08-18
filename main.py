"""
Lexia AI Agent Starter Kit
==========================

A production-ready starter kit for building AI agents that integrate with the Lexia platform.
This demonstrates best practices for creating AI agents with proper memory management,
streaming responses, file processing, and function calling capabilities.

Key Features:
- Clean, maintainable architecture with separation of concerns
- Built-in conversation memory and thread management
- Support for image analysis
- Real-time response streaming via Lexia's infrastructure
- Robust error handling and comprehensive logging
- Inherited endpoints from Lexia package for consistency

Architecture:
- Main processing logic in process_message() function
- Memory management via ConversationManager class
- Utility functions for OpenAI integration
- Standard Lexia endpoints inherited from package

Usage:
    python main.py

The server will start on http://localhost:8000 with the following endpoints:
- POST /api/v1/send_message - Main chat endpoint
- GET /api/v1/health - Health check
- GET /api/v1/ - Root information
- GET /api/v1/docs - Interactive API documentation

Author: Lexia Team
License: MIT
"""

import logging
from openai import OpenAI
import os
import requests

# Configure logging with informative format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import AI agent components
from memory import ConversationManager
from lexia import (
    LexiaHandler, 
    ChatResponse, 
    ChatMessage, 
    Variable, 
    create_success_response,
    create_lexia_app,
    add_standard_endpoints
)
from agent_utils import format_system_prompt, format_messages_for_openai
from lexia.utils import set_env_variables, get_openai_api_key

# Initialize core services
conversation_manager = ConversationManager(max_history=10)  # Keep last 10 messages per thread
lexia = LexiaHandler()

# Create the FastAPI app using Lexia's web utilities
app = create_lexia_app(
    title="Lexia AI Agent Starter Kit",
    version="1.0.0",
    description="Production-ready AI agent starter kit with Lexia integration"
)

async def process_message(data: ChatMessage) -> None:
    """
    Process incoming chat messages using OpenAI and send responses via Lexia.
    
    This is the core AI processing function that you can customize for your specific use case.
    The function handles:
    1. Message validation and logging
    2. Environment variable setup
    3. OpenAI API communication
    4. File processing (images)
    5. Response streaming and completion
    
    Args:
        data: ChatMessage object containing the incoming message and metadata
        
    Returns:
        None: Responses are sent via Lexia's streaming and completion APIs
        
    Raises:
        Exception: If message processing fails (errors are sent to Lexia)
        
    Customization Points:
        - Modify system prompts and context
        - Adjust OpenAI model parameters
        - Implement specialized file processing
        - Customize error handling and logging
    """
    try:
        # Log comprehensive request information for debugging
        logger.info("=" * 80)
        logger.info("📥 FULL REQUEST BODY RECEIVED:")
        logger.info("=" * 80)
        logger.info(f"Thread ID: {data.thread_id}")
        logger.info(f"Message: {data.message}")
        logger.info(f"Response UUID: {data.response_uuid}")
        logger.info(f"Model: {data.model}")
        logger.info(f"System Message: {data.system_message}")
        logger.info(f"Project System Message: {data.project_system_message}")
        logger.info(f"Variables: {data.variables}")
        logger.info(f"Stream URL: {getattr(data, 'stream_url', 'Not provided')}")
        logger.info(f"Stream Token: {getattr(data, 'stream_token', 'Not provided')}")
        logger.info(f"Full data object: {data}")
        logger.info("=" * 80)
        
        # Log key processing information
        logger.info(f"🚀 Processing message for thread {data.thread_id}")
        logger.info(f"📝 Message: {data.message[:100]}...")
        logger.info(f"🔑 Response UUID: {data.response_uuid}")
        
        # Set environment variables and get OpenAI API key
        set_env_variables(data.variables)
        openai_api_key = get_openai_api_key(data.variables)
        if not openai_api_key:
            error_msg = "OpenAI API key not found in variables"
            logger.error(error_msg)
            lexia.send_error(data, error_msg)
            return
        
        # Initialize OpenAI client and conversation management
        client = OpenAI(api_key=openai_api_key)
        conversation_manager.add_message(data.thread_id, "user", data.message)
        thread_history = conversation_manager.get_history(data.thread_id)
        
        # Format system prompt and messages for OpenAI
        system_prompt = format_system_prompt(data.system_message, data.project_system_message)
        messages = format_messages_for_openai(system_prompt, thread_history, data.message)
        
        # Process image files if present
        if hasattr(data, 'file_type') and data.file_type == 'image' and hasattr(data, 'file_url') and data.file_url:
            logger.info(f"🖼️ Image detected: {data.file_url}")
            # Add image to the last user message for vision analysis
            if messages and messages[-1]['role'] == 'user':
                messages[-1]['content'] = [
                    {"type": "text", "text": messages[-1]['content']},
                    {"type": "image_url", "image_url": {"url": data.file_url}}
                ]
                logger.info("🖼️ Image added to OpenAI request for vision analysis")
        
        # Log OpenAI request details
        logger.info(f"🤖 Sending to OpenAI model: {data.model}")
        logger.info(f"💬 System prompt: {system_prompt[:100]}...")
        logger.info(f"📤 Messages being sent to OpenAI: {messages}")
        
        # Stream response from OpenAI
        stream = client.chat.completions.create(
            model=data.model,
            messages=messages,
            max_tokens=1000,
            temperature=0.7,
            stream=True
        )
        
        # Process streaming response
        full_response = ""
        usage_info = None
        
        logger.info("📡 Streaming response from OpenAI...")
        
        for chunk in stream:
            # Handle content chunks
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                # Stream chunk to Lexia via Centrifugo
                lexia.stream_chunk(data, content)
            
            # Capture usage information from the last chunk
            if chunk.usage:
                usage_info = chunk.usage
                logger.info(f"📊 Usage info captured: {usage_info}")
        
        logger.info(f"✅ OpenAI response complete. Length: {len(full_response)} characters")
        
        # Store response in conversation memory
        conversation_manager.add_message(data.thread_id, "assistant", full_response)
        
        # Send complete response to Lexia
        logger.info("📤 Sending complete response to Lexia...")
        lexia.complete_response(data, full_response, usage_info)
        
        logger.info(f"🎉 Message processing completed successfully for thread {data.thread_id}")
            
    except Exception as e:
        error_msg = f"Error processing message: {str(e)}"
        logger.error(error_msg, exc_info=True)
        lexia.send_error(data, error_msg)


# Add standard Lexia endpoints including the inherited send_message endpoint
# This provides all the standard functionality without additional code
add_standard_endpoints(
    app, 
    conversation_manager=conversation_manager,
    lexia_handler=lexia,
    process_message_func=process_message
)

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting Lexia AI Agent Starter Kit...")
    print("=" * 60)
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/health")
    print("💬 Chat Endpoint: http://localhost:8000/api/v1/send_message")
    print("=" * 60)
    print("\n✨ This starter kit demonstrates:")
    print("   - Clean integration with Lexia package")
    print("   - Inherited endpoints for common functionality")
    print("   - Customizable AI message processing")
    print("   - Conversation memory management")
    print("   - File processing (images)")
    print("   - Proper data structure for Lexia communication")
    print("   - Comprehensive error handling and logging")
    print("\n🔧 Customize the process_message() function to add your AI logic!")
    print("=" * 60)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
