"""
Lexia AI Agent Starter Kit - Food Menu Analyzer with Photo Search
================================================================

A production-ready starter kit for building AI agents that integrate with the Lexia platform.
This demonstrates best practices for creating AI agents with proper memory management,
streaming responses, file processing, and function calling capabilities.

Key Features:
- Clean, maintainable architecture with separation of concerns
- Built-in conversation memory and thread management
- Specialized food menu image analysis
- Internet photo search using Serper API
- Real-time response streaming via Lexia's infrastructure
- Robust error handling and comprehensive logging
- Inherited endpoints from Lexia package for consistency

Food Menu Analysis:
- Automatically detects when images are uploaded
- Specialized system prompt for food menu analysis
- Extracts food names from valid menus
- Searches internet for food photos using Serper API
- Returns food names with clickable photo URLs
- Declines non-food menu images with specific message
- Focused and concise responses

Serper API Integration:
- Automatically searches for food photos on the internet
- Uses SERPER_API_KEY from Lexia variables
- Returns clickable photo URLs for each food item
- Handles API errors gracefully
- Limits search to first 10 food items for performance

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
        
        # Process image files if present
        if hasattr(data, 'file_type') and data.file_type == 'image' and hasattr(data, 'file_url') and data.file_url:
            logger.info(f"🖼️ Image detected: {data.file_url}")
            
            # Create specialized system prompt for food menu analysis
            food_menu_system_prompt = """You are a specialized food menu analyzer. Your ONLY job is to:

1. Analyze the image to determine if it contains a food menu
2. If it's a food menu: Extract ONLY the names of the food items/dishes
3. If it's NOT a food menu: Respond with exactly "This is not a food menu. It's not my area of interest."

Important rules:
- Only respond to food menus
- For food menus, extract ONLY food names (no descriptions, prices, or other details)
- For non-food menus, use the exact phrase above
- Be concise and direct
- Do not provide any other information or explanations
- Do not ask questions or engage in conversation
- Focus solely on identifying food items from menus
- Return food names in a simple list format"""

            logger.info("🍽️ Food menu analysis mode activated")
            logger.info("📋 System prompt updated for specialized food menu analysis")
            
            # Format messages for OpenAI with food menu analysis
            messages = [{"role": "system", "content": food_menu_system_prompt}]
            
            # Add conversation history (excluding timestamp)
            for msg in thread_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Add current user message with image
            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": "Please analyze this image and tell me if it's a food menu. If it is, extract the food names. If not, say it's not your area of interest."},
                    {"type": "image_url", "image_url": {"url": data.file_url}}
                ]
            })
            
            logger.info("🖼️ Image added to OpenAI request for food menu analysis")
            logger.info("🍽️ Using specialized food menu analysis system prompt")
            
            # Set system_prompt for logging
            system_prompt = food_menu_system_prompt
        else:
            # For non-image messages, use the original system prompt and message formatting
            system_prompt = format_system_prompt(data.system_message, data.project_system_message)
            messages = format_messages_for_openai(system_prompt, thread_history, data.message)
        
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
        
        # Suppress streaming to Lexia for image messages to avoid partial lists without URLs
        is_image_message = hasattr(data, 'file_type') and data.file_type == 'image' and hasattr(data, 'file_url') and data.file_url

        for chunk in stream:
            # Handle content chunks
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                # Stream chunk to Lexia via Centrifugo
                if not is_image_message:
                    lexia.stream_chunk(data, content)
            
            # Capture usage information from the last chunk
            if chunk.usage:
                usage_info = chunk.usage
                logger.info(f"📊 Usage info captured: {usage_info}")
        
        logger.info(f"✅ OpenAI response complete. Length: {len(full_response)} characters")
        
        # Process food menu response and search for food photos if applicable
        if hasattr(data, 'file_type') and data.file_type == 'image' and hasattr(data, 'file_url') and data.file_url:
            if "This is not a food menu" not in full_response:
                logger.info("🍽️ Food menu detected, searching for food photos...")
                
                # Extract food names from the response
                # FIXED: Previously excluded lines starting with '-', '•', '*' which are the actual food names
                # Now properly processes all lines and removes list markers to extract food names
                food_names = []
                lines = full_response.strip().split('\n')
                logger.info(f"🔍 Processing {len(lines)} lines from OpenAI response")
                
                for line in lines:
                    line = line.strip()
                    if line:  # Process any non-empty line
                        logger.info(f"📝 Processing line: '{line}'")
                        
                        # Remove list markers and clean up the line
                        food_name = line
                        # Remove common list markers
                        for marker in ['- ', '• ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ', '10. ']:
                            if food_name.startswith(marker):
                                food_name = food_name[len(marker):]
                                logger.info(f"  🏷️ Removed marker '{marker}', result: '{food_name}'")
                                break
                        
                        # Clean up the food name by removing common suffixes and prefixes
                        food_name = food_name.split(':')[0].split('-')[0].split('(')[0].split('[')[0].strip()
                        logger.info(f"  🧹 After cleanup: '{food_name}'")
                        
                        # Remove numbers and common words
                        food_name = ' '.join([word for word in food_name.split() if not word.isdigit() and word.lower() not in ['the', 'a', 'an', 'and', 'or', 'with', 'of', 'in', 'on', 'at', 'to', 'for']])
                        logger.info(f"  🔤 After word filtering: '{food_name}'")
                        
                        # Only add if it's a valid food name
                        if food_name and len(food_name) > 2 and not food_name.lower() in ['menu', 'food', 'dish', 'item', 'price', 'description', 's', 'es']:
                            food_names.append(food_name)
                            logger.info(f"  ✅ Added food name: '{food_name}'")
                        else:
                            logger.info(f"  ❌ Rejected: '{food_name}' (length: {len(food_name) if food_name else 0})")
                
                logger.info(f"🍕 Extracted food names: {food_names}")
                
                # Search for food photos using Serper API
                # This integration searches the internet for photos of each food item
                # and returns clickable URLs that users can view in their browser
                # Results are formatted in markdown for better presentation
                if food_names:
                    # Get Serper API key from variables
                    serper_api_key = None
                    for var in data.variables:
                        if var.name == "SERPER_API_KEY":
                            serper_api_key = var.value
                            break
                    
                    if serper_api_key:
                        logger.info("🔍 Using Serper API to search for food photos...")
                        
                        # Stream header first
                        # NEW: Stream each food item with photo URL as soon as it's found
                        # This provides real-time feedback to users instead of waiting for all searches
                        header_message = "# 🍽️ Food Menu Analysis Results\n\n"
                        lexia.stream_chunk(data, header_message)
                        
                        for food_name in food_names[:10]:  # Limit to first 10 items
                            try:
                                # Search for food photos using Serper Images API
                                search_url = "https://google.serper.dev/images"
                                headers = {
                                    "X-API-KEY": serper_api_key,
                                    "Content-Type": "application/json"
                                }
                                search_data = {
                                    "q": f"{food_name} food photo",
                                    "num": 1
                                }
                                
                                response = requests.post(search_url, headers=headers, json=search_data, timeout=10)
                                
                                if response.status_code == 200:
                                    search_results = response.json()
                                    # Serper Images API returns results under 'images'
                                    food_photo_url = ''
                                    if 'images' in search_results and search_results['images']:
                                        first_result = search_results['images'][0]
                                        food_photo_url = first_result.get('imageUrl') or first_result.get('thumbnailUrl') or first_result.get('link') or ''
                                    
                                    # Stream this food item immediately with markdown formatting
                                    if food_photo_url:
                                        food_item_message = f"## 🍕 {food_name}\n\n📸 **[View Photo]({food_photo_url})**\n\n---\n\n"
                                        lexia.stream_chunk(data, food_item_message)
                                        logger.info(f"✅ Found and streamed photo for {food_name}: {food_photo_url}")
                                    else:
                                        food_item_message = f"## 🍕 {food_name}\n\n📸 *No photo found*\n\n---\n\n"
                                        lexia.stream_chunk(data, food_item_message)
                                        logger.info(f"⚠️ No photo found for {food_name}")
                                else:
                                    food_item_message = f"## 🍕 {food_name}\n\n📸 *Search failed (Status: {response.status_code})*\n\n---\n\n"
                                    lexia.stream_chunk(data, food_item_message)
                                    logger.warning(f"❌ Serper API search failed for {food_name}: {response.status_code}")
                                    
                            except requests.exceptions.Timeout:
                                food_item_message = f"## 🍕 {food_name}\n\n📸 *Search timeout*\n\n---\n\n"
                                lexia.stream_chunk(data, food_item_message)
                                logger.warning(f"⏰ Serper API timeout for {food_name}")
                            except requests.exceptions.RequestException as e:
                                food_item_message = f"## 🍕 {food_name}\n\n📸 *Search error*\n\n---\n\n"
                                lexia.stream_chunk(data, food_item_message)
                                logger.error(f"❌ Request error for {food_name}: {str(e)}")
                            except Exception as e:
                                food_item_message = f"## 🍕 {food_name}\n\n📸 *Search error*\n\n---\n\n"
                                lexia.stream_chunk(data, food_item_message)
                                logger.error(f"❌ Unexpected error for {food_name}: {str(e)}")
                        
                        # No need to build enhanced_response since we're streaming everything
                        # Just set full_response to indicate completion
                        full_response = "🍽️ Food menu analysis completed with photo search results."
                        logger.info("🎉 All food items streamed with photo search results")
                    else:
                        logger.warning("⚠️ SERPER_API_KEY not found in variables, sending basic food list")
                        # Stream basic food list with markdown formatting
                        header_message = "# 🍽️ Food Menu Items\n\n"
                        lexia.stream_chunk(data, header_message)
                        
                        for food_name in food_names:
                            food_item_message = f"## 🍕 {food_name}\n\n---\n\n"
                            lexia.stream_chunk(data, food_item_message)
                        
                        full_response = "🍽️ Basic food menu list completed."
                else:
                    logger.info("⚠️ No food names extracted from response")
        
        # Build complete response content for Lexia completion
        # This is necessary because Lexia needs the complete content for:
        # 1. Conversation memory storage
        # 2. Final completion signal
        # 3. Proper conversation flow management
        if hasattr(data, 'file_type') and data.file_type == 'image' and hasattr(data, 'file_url') and data.file_url:
            if "This is not a food menu" not in full_response:
                # Build the complete markdown response for conversation memory and completion
                complete_content = "# 🍽️ Food Menu Analysis Results\n\n"
                
                if food_names:
                    for food_name in food_names[:10]:
                        complete_content += f"## 🍕 {food_name}\n\n"
                        # Note: We can't include the actual photo URLs here since they were streamed separately
                        # But we can indicate that photos were searched for
                        complete_content += f"📸 *Photo search completed*\n\n---\n\n"
                    
                    complete_content += "\n*All food items have been analyzed and photos searched via Serper API.*"
                else:
                    complete_content += "*No food names could be extracted from the menu.*"
                
                full_response = complete_content
                logger.info("📋 Complete response content built for Lexia completion")
        
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
    
    print("🚀 Starting Lexia AI Agent Starter Kit - Food Menu Analyzer with Photo Search...")
    print("=" * 60)
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/v1/health")
    print("💬 Chat Endpoint: http://localhost:8000/api/v1/send_message")
    print("=" * 60)
    print("\n✨ This starter kit demonstrates:")
    print("   - Clean integration with Lexia package")
    print("   - Inherited endpoints for common functionality")
    print("   - Specialized food menu image analysis")
    print("   - Internet photo search using Serper API")
    print("   - Conversation memory management")
    print("   - File processing (images)")
    print("   - Proper data structure for Lexia communication")
    print("   - Comprehensive error handling and logging")
    print("\n🍽️ Food Menu Analysis Features:")
    print("   - Automatically detects food menu images")
    print("   - Extracts food names from menus")
    print("   - Searches internet for food photos")
    print("   - Returns clickable photo URLs")
    print("   - Declines non-food menu images")
    print("   - Focused and concise responses")
    print("\n🔍 Serper API Integration:")
    print("   - Internet photo search for food items")
    print("   - Uses SERPER_API_KEY from Lexia variables")
    print("   - Enhanced responses with photo links")
    print("\n🔧 Customize the process_message() function to add your AI logic!")
    print("=" * 60)
    
    # Start the FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8000)
