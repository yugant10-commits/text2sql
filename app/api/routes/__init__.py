# app/api/routes/chat.py
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from app.services.openai_service import OpenAIService
from app.services.sql_service import SQLService
import datetime

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.post("/query")
async def process_query(
    request: Request,
    query: str = Form(...),
    openai_service: OpenAIService = Depends(),
    sql_service: SQLService = Depends()
):
    try:
        json_output = await openai_service.process_first_call(query)
        sql_query = await openai_service.process_second_call(json_output)
        sql_query = sql_query.strip().replace("```sql", "").replace("```", "").strip()

        columns, results = await sql_service.execute_query(sql_query)

        return templates.TemplateResponse(
            "components/message.html",
            {
                "request": request,
                "user_query": query,
                "sql_query": sql_query,
                "columns": columns,
                "results": results,
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            }
        )
    except Exception as e:
        return templates.TemplateResponse(
            "components/error_message.html",
            {
                "request": request,
                "user_query": query,
                "error": str(e),
                "timestamp": datetime.datetime.now().strftime("%H:%M")
            }
        )