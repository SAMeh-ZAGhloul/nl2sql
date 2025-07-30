
import os
import sqlite3
import pandas as pd
from flask import Flask, request, render_template
import google.generativeai as genai

app = Flask(__name__)
DB_PATH = "hr.db"

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

def get_schema_info():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    tables = {}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    for (table,) in cursor.fetchall():
        cursor.execute(f"PRAGMA table_info({table});")
        cols = [col[1] for col in cursor.fetchall()]
        tables[table] = cols
    conn.close()
    return tables

def nl_to_sql(question, schema_description):
    prompt = f"""
You are a SQL expert working with the following SQLite schema:

{schema_description}

Convert the following natural language question to an SQLite query:

Question: {question}

SQL:
"""
    response = model.generate_content(prompt)
    return response.text.strip()

def execute_sql(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@app.route("/", methods=["GET", "POST"])
def index():
    result = query = error = None
    schema = get_schema_info()

    if request.method == "POST":
        question = request.form["question"]
        schema_text = "\n".join(
            [f"Table: {table}\n- " + ", ".join(columns) for table, columns in schema.items()]
        )
        try:
            query = nl_to_sql(question, schema_text)
            result = execute_sql(query).to_html(classes="table table-bordered", index=False)
        except Exception as e:
            error = str(e)

    return render_template("index.html", query=query, result=result, error=error, schema=schema)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5555)
