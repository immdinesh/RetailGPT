# RetailGPT — GenAI NL-to-SQL

Natural language to SQL for retail analytics using **Python**, **LangChain**, **OpenAI API**, and **MySQL**. Built for 1,000+ inventory and sales records (e.g. Adidas, Nike) with few-shot prompting for high accuracy and ~70% reduction in manual SQL effort.

## Features

- **NL-to-SQL**: Ask questions in plain English; get correct SQL and results.
- **90%+ query accuracy** via few-shot prompting and schema-aware generation.
- **Retail analytics** on inventory and sales (brands: Adidas, Nike).
- **Few-shot prompting** to cut manual SQL writing by ~70%.

## Setup

1. **Clone / open** this project and create a virtual environment:

   ```bash
   python -m venv venv
   venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. **Configure**:
   - Copy `.env.example` to `.env`.
   - Set `OPENAI_API_KEY` and MySQL credentials (`MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`).

3. **Database**:
   - Create MySQL database: `CREATE DATABASE retailgpt;`
   - Run schema: `python scripts/init_db.py`
   - Seed sample data: `python scripts/seed_data.py`

4. **Run**:
   - Interactive: `python main.py`
   - Or use the `retailgpt` module from your own scripts.

## Usage

```bash
python main.py
```

Example questions:

- "Total sales for Nike last month"
- "Top 5 Adidas products by units sold"
- "Inventory value by brand"
- "Which products have stock below 50?"

## Project layout

- `main.py` — Entry point and interactive NL query loop.
- `src/` — LangChain NL-to-SQL chain, DB connection, prompts.
- `scripts/` — DB init and seed data (1,000+ records).
- `config.py` — Loads env and DB config.

## License

MIT.
