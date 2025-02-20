from app.utils.openai_handler import AsyncOpenAIHandler
from app.services.new_prompt import system_message_first, schema_first, another_prompt

class OpenAIService:
    def __init__(self):
        self.handler = AsyncOpenAIHandler()

    async def process_first_call(self, query: str):
        return await self.handler.process_first_call(
            query,
            system_message_first,
            schema_first
        )

    async def process_second_call(self, json_output: dict):
        return await self.handler.process_second_call(
            str(json_output),
            another_prompt
        )
        
import asyncio
# from app.sql_generator.new_prompt import schema_first, system_message_first, another_prompt
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
async def main():
    # Initialize the OpenAI service
    service = OpenAIService()
    
    try:
        # Example natural language query
        query = "Show me all flights from London to Paris in January 2024"
        
        # First call - Convert to structured JSON
        logger.info(f"Processing query: {query}")
        json_output = await service.process_first_call(query)
        logger.info(f"JSON output: {json_output}")
        
        # Second call - Generate SQL
        sql_query = await service.process_second_call(json_output)
        logger.info(f"Generated SQL: {sql_query}")
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())