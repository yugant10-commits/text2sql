# app/api/routes/chat.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import StreamingResponse
from app.services.openai_service import OpenAIService
from app.services.sql_service import SQLService
import datetime
import asyncio

router = APIRouter(prefix="")  # Empty prefix for root-level routes

# Update templates directory path
templates = Jinja2Templates(directory="app/templates")

@router.post("/query")
async def process_query(
    request: Request,
    query: str = Form(...),
    openai_service: OpenAIService = Depends(),
    sql_service: SQLService = Depends()
):
    async def generate_response():
        try:
            # Step 1: JSON Analysis
            json_output = await openai_service.process_first_call(query)
            yield templates.TemplateResponse(
                "components/step1.html",
                {
                    "request": request,
                    "json_output": json_output,
                }
            ).body.decode() + "\n\n"
            await asyncio.sleep(0.5)

            # Step 2: SQL Generation
            sql_query = await openai_service.process_second_call(json_output)
            sql_query = sql_query.strip().replace("```sql", "").replace("```", "").strip()
            yield templates.TemplateResponse(
                "components/step2.html",
                {
                    "request": request,
                    "sql_query": sql_query,
                }
            ).body.decode() + "\n\n"
            await asyncio.sleep(0.5)

            # Step 3: Query Execution
            columns, results = await sql_service.execute_query(sql_query)
            yield templates.TemplateResponse(
                "components/step3.html",
                {
                    "request": request,
                    "columns": columns,
                    "results": results,
                }
            ).body.decode() + "\n\n"

        except Exception as e:
            yield templates.TemplateResponse(
                "components/error_message.html",
                {
                    "request": request,
                    "error": str(e),
                }
            ).body.decode() + "\n\n"

    return StreamingResponse(
        generate_response(),
        media_type="text/event-stream"
    )