from openai import AsyncOpenAI
import json
import logging
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import asyncio
from dataclasses import dataclass
# from new_prompt import system_message_first, schema_first, another_prompt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OpenAIException(Exception):
    """Custom exception for OpenAI related errors"""
    pass

@dataclass
class OpenAIConfig:
    """Configuration for OpenAI API calls"""
    model: str
    temperature: float = 0.1
    max_tokens: int = 1500
    system_message: str = ""
    response_format: Optional[Dict] = None

class AsyncOpenAIHandler:
    """Handles AsyncOpenAI API calls with retry mechanism and error handling"""
    
    def __init__(self):
        """Initialize AsyncOpenAI client with API key"""
        load_dotenv()
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise OpenAIException("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    async def _make_api_call(self, 
                            input_text: str, 
                            config: OpenAIConfig) -> Any:
        """Make async API call to OpenAI with retry mechanism"""
        try:
            messages = [
                {"role": "system", "content": config.system_message},
                {"role": "user", "content": input_text}
            ]
            
            completion_params = {
                "model": config.model,
                "messages": messages,
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
            
            if config.response_format:
                completion_params["response_format"] = config.response_format
                
            completion = await self.client.chat.completions.create(**completion_params)
            return completion.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in OpenAI API call: {str(e)}")
            raise OpenAIException(f"Failed to get response from OpenAI: {str(e)}")

    async def process_first_call(self, 
                                input_text: str, 
                                system_message: str,
                                schema: Dict) -> Dict:
        """Process first OpenAI call with JSON schema validation"""
        config = OpenAIConfig(
            model="gpt-4o-mini",
            system_message=system_message,
            response_format={
                "type": "json_schema",
                "json_schema": schema,
            }
        )
        
        try:
            response = await self._make_api_call(input_text, config)
            return json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise OpenAIException("Invalid JSON response from OpenAI")

    async def process_second_call(self, 
                                 input_text: str, 
                                 system_message: str) -> str:
        """Process second OpenAI call for SQL generation"""
        config = OpenAIConfig(
            model="gpt-4o-mini",
            system_message=system_message
        )
        
        return await self._make_api_call(input_text, config)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()

async def main():
    # Define your schema and system messages
    try:
        async with AsyncOpenAIHandler() as handler:
            # First call - Convert to JSON
            json_output = await handler.process_first_call(
                "Show me all flights from London to Paris",
                system_message_first,
                schema_first
            )
            
            # Second call - Generate SQL
            sql_query = await handler.process_second_call(
                str(json_output),
                another_prompt
            )
            
            print(f"Generated SQL: {sql_query}")
            
    except OpenAIException as e:
        print(f"Error: {str(e)}")

# Run the example
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
