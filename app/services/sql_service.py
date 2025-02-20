from app.utils.database import DatabaseConnection
from app.utils.validator import SQLValidator

class SQLService:
    def __init__(self):
        self.db = DatabaseConnection()

    async def execute_query(self, sql_query: str):
        validator = SQLValidator(sql_query)
        valid, validated_query = validator.is_valid()
        print(f"Validated query... {validated_query}")
        
        if not valid:
            raise ValueError(validated_query)
            
        return self.db.execute_query(validated_query)