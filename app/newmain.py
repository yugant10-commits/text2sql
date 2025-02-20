from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import sqlite3
import datetime

from app.utils.openai_handler import first_openai_call, second_openai_call
from sql_generator.run_sql_query import run_query
from utils.validator import SQLValidator
from utils.database import DatabaseConnection

db = DatabaseConnection() 
app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/query")
async def process_query(request: Request, query: str = Form(...)):
    """This API endpoint is used to accept query from the user and return valid answers from the database or error."""    
    json_output = first_openai_call(query)
    sql_query = second_openai_call(json_output)
    sql_query = sql_query.strip().replace("```sql", "").replace("```", "").strip()

    
    try:
        try:
            print(f"sql query: {sql_query}")
            sql_validator= SQLValidator(sql_query)
            valid_bool, valid_sql_query = sql_validator.is_valid()
            print(f"sql validator: {valid_sql_query}")
            if not valid_bool:
                columns, results = db.execute_query(valid_sql_query)
                print(f"result: {results}")
        except Exception as e:
            columns, results = 'Error', str(e)
            print(e)
        # Return the message component
        return templates.TemplateResponse(
            "components/message.html",
            {
                "request": request,
                "user_query": query,
                "sql_query": sql_query,
                "columns": results[0],
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
