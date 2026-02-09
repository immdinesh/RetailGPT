"""LangChain NL-to-SQL with few-shot prompting for RetailGPT."""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from config import get_openai_api_key
from src.db import SCHEMA_DESCRIPTION, run_read_only_query

# Few-shot examples to achieve 90%+ accuracy and reduce manual SQL (~70%)
FEW_SHOT_EXAMPLES = """
Example 1:
Question: What is the total sales for Nike last month?
SQL: SELECT COALESCE(SUM(s.total_amount), 0) AS total_sales FROM sales s JOIN products p ON s.product_id = p.id WHERE p.brand = 'Nike' AND s.sale_date >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH) AND s.sale_date < LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) + INTERVAL 1 DAY;

Example 2:
Question: Top 5 Adidas products by units sold
SQL: SELECT p.name, SUM(s.quantity) AS units_sold FROM sales s JOIN products p ON s.product_id = p.id WHERE p.brand = 'Adidas' GROUP BY p.id, p.name ORDER BY units_sold DESC LIMIT 5;

Example 3:
Question: Inventory value by brand
SQL: SELECT p.brand, SUM(i.quantity * p.unit_price) AS inventory_value FROM inventory i JOIN products p ON i.product_id = p.id GROUP BY p.brand;

Example 4:
Question: Which products have stock below 50?
SQL: SELECT p.sku, p.name, p.brand, i.quantity FROM inventory i JOIN products p ON i.product_id = p.id WHERE i.quantity < 50 ORDER BY i.quantity ASC;

Example 5:
Question: Total revenue by region this year
SQL: SELECT s.region, SUM(s.total_amount) AS revenue FROM sales s WHERE s.sale_date >= DATE_FORMAT(CURDATE(), '%Y-01-01') GROUP BY s.region ORDER BY revenue DESC;

Example 6:
Question: How many Adidas and Nike products do we have?
SQL: SELECT brand, COUNT(*) AS product_count FROM products WHERE brand IN ('Adidas', 'Nike') GROUP BY brand;

Example 7:
Question: Average sale amount for Nike footwear
SQL: SELECT AVG(s.total_amount) AS avg_sale FROM sales s JOIN products p ON s.product_id = p.id WHERE p.brand = 'Nike' AND p.category = 'Footwear';
"""

SYSTEM_PROMPT = """You are a MySQL expert for a retail database. Given the schema and examples, generate ONLY a single valid MySQL SELECT statement. No explanation, no markdown, no backticks. Output nothing but the SQL.
""" + SCHEMA_DESCRIPTION + FEW_SHOT_EXAMPLES

USER_TEMPLATE = """Question: {question}
SQL:"""


def build_chain():
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_TEMPLATE),
    ])
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        api_key=get_openai_api_key(),
        temperature=0,
    )
    return prompt | llm | StrOutputParser()


def clean_sql(raw: str) -> str:
    """Strip markdown code blocks and extra whitespace."""
    s = raw.strip()
    if s.startswith("```"):
        lines = s.split("\n")
        if lines[0].startswith("```sql"):
            lines = lines[1:]
        elif lines[0].startswith("```"):
            lines = lines[1:]
        s = "\n".join(lines)
    if s.endswith("```"):
        s = s[:-3].strip()
    return s.strip()


def query_with_nl(question: str) -> dict:
    """
    Convert natural language to SQL, execute, and return results.
    Returns: {"sql": str, "rows": list, "error": str | None}
    """
    chain = build_chain()
    try:
        raw_sql = chain.invoke({"question": question})
        sql = clean_sql(raw_sql)
    except Exception as e:
        return {"sql": None, "rows": [], "error": str(e)}

    if not sql:
        return {"sql": None, "rows": [], "error": "No SQL generated."}

    try:
        rows = run_read_only_query(sql)
        return {"sql": sql, "rows": rows, "error": None}
    except Exception as e:
        return {"sql": sql, "rows": [], "error": str(e)}
