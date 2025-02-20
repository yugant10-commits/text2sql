import re
import logging
import sqlparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLValidator:
    """
    A class that validates SQL queries, ensuring:
    - Queries are SELECT-only.
    - No disallowed keywords (e.g., INSERT, UPDATE, DELETE).
    - Balanced quotes.
    - No multiple statements.
    - Query does not retrieve more than 10 rows (enforces LIMIT 10).
    """

    DISALLOWED_KEYWORDS = {"insert", "update", "delete", "drop", "alter", "create"}
    LIMIT_PATTERN = re.compile(r'\blimit\s+(\d+)', re.IGNORECASE)
    
    def __init__(self, query: str):
        self.original_query = query.strip()
        self.modified_query = query.strip()
    
    def is_valid(self):
        """
        Runs all validation checks on the query.
        Returns (bool, str) where:
        - True, modified_query if the query is valid.
        - False, error_message if the query is invalid.
        """
        if not self._is_non_empty():
            return False, "Query must be a non-empty string"
        if not self._is_select_query():
            return False, "Only SELECT queries are allowed"
        if not self._has_balanced_quotes():
            return False, "Query has unbalanced quotes"
        if not self._is_single_statement():
            return False, "Multiple SQL statements are not allowed"
        if self._contains_disallowed_keywords():
            return False, "Query contains disallowed keywords"
        if not self._is_syntactically_valid():
            return False, "Query failed basic syntax validation"
        
        self._enforce_limit()
        return True, self.modified_query

    def _is_non_empty(self):
        """Ensure the query is a non-empty string."""
        return isinstance(self.original_query, str) and bool(self.original_query.strip())

    def _is_select_query(self):
        """Ensure the query starts with SELECT."""
        return self.original_query.lower().startswith("select")

    def _has_balanced_quotes(self):
        """Ensure quotes (single and double) are balanced."""
        return self.original_query.count("'") % 2 == 0 and self.original_query.count('"') % 2 == 0

    def _is_single_statement(self):
        """Ensure the query does not contain multiple statements."""
        semicolon_count = self.original_query.count(";")
        return semicolon_count <= 1 and (semicolon_count == 0 or self.original_query.endswith(";"))

    def _contains_disallowed_keywords(self):
        """Check for unsafe SQL keywords (e.g., INSERT, UPDATE, DELETE)."""
        for keyword in self.DISALLOWED_KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', self.original_query, re.IGNORECASE):
                logger.warning(f"Disallowed keyword found: {keyword}")
                return True
        return False

    def _is_syntactically_valid(self):
        """Use sqlparse to perform basic syntax validation."""
        try:
            parsed = sqlparse.parse(self.original_query)
            return bool(parsed) and len(parsed) > 0
        except Exception as e:
            logger.exception("Error parsing query")
            return False

    def _enforce_limit(self):
        """Modify the query to enforce LIMIT 10."""
        match = self.LIMIT_PATTERN.search(self.modified_query)
        if match:
            current_limit = int(match.group(1))
            if current_limit > 10:
                self.modified_query = self.LIMIT_PATTERN.sub("LIMIT 10", self.modified_query)
        else:
            # Append LIMIT 10 before any trailing semicolon or at the end.
            if self.modified_query.endswith(";"):
                self.modified_query = self.modified_query[:-1] + " LIMIT 10;"
            else:
                self.modified_query += " LIMIT 10"

# # Example Usage
# if __name__ == "__main__":
#     queries = [
#         "SELECT * FROM users;",         # Valid (appends LIMIT 10)
#         "SELECT * FROM orders LIMIT 5;", # Valid (limit is within bounds)
#         "SELECT * FROM products LIMIT 20;", # Modified to LIMIT 10
#         "DELETE FROM users;",           # Invalid (not SELECT)
#         "SELECT * FROM customers"        # Valid (appends LIMIT 10)
#     ]

#     for q in queries:
#         validator = SQLValidator(q)
#         is_valid, result = validator.is_valid()
#         print("Query:", q)
#         print("Valid:", is_valid)
#         print("Result:", result)
#         print("=" * 50)
