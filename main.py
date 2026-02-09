"""
RetailGPT — GenAI NL-to-SQL for retail analytics.
Run: python main.py
"""
from src.nl_to_sql import query_with_nl


def main():
    print("RetailGPT — Natural language to SQL (Adidas / Nike inventory & sales)")
    print("Enter a question or 'quit' to exit.\n")
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            break
        result = query_with_nl(question)
        if result["error"]:
            print(f"Error: {result['error']}")
            if result["sql"]:
                print(f"Generated SQL: {result['sql']}")
        else:
            print(f"SQL: {result['sql']}\n")
            rows = result["rows"]
            if not rows:
                print("(No rows)")
            else:
                print("Results:")
                for i, row in enumerate(rows[:50], 1):
                    print(f"  {i}. {row}")
                if len(rows) > 50:
                    print(f"  ... and {len(rows) - 50} more rows")
            print()
    print("Goodbye.")


if __name__ == "__main__":
    main()
