import os
import sqlite3
import pandas as pd
from flask import Flask, request, render_template
import requests

# Configure the API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set!")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

app = Flask(__name__)
DB_PATH = "hr.db"

schema_description = """
Table: employees
- employee_id (PK)
- first_name
- last_name
- email
- phone_number
- hire_date
- job_id (FK to jobs.job_id)
- salary
- department_id (FK to departments.department_id)
- manager_id (FK to employees.employee_id)

Table: departments
- department_id (PK)
- department_name
- location_id (FK to locations.location_id)

Table: jobs
- job_id (PK)
- job_title
- min_salary
- max_salary

Table: locations
- location_id (PK)
- city
- state_province
- country_id (FK to countries.country_id)

Table: countries
- country_id (PK)
- country_name
"""

def nl_to_sql(question, schema_description):
    prompt = f"""
You are a SQL expert working with the following SQLite schema:

{schema_description}

Convert the following natural language question to an SQLite query:

Question: {question}

SQL:
"""
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    response = requests.post(
        GEMINI_ENDPOINT,
        headers=headers,
        json={
            "model": "gemini-2.0-flash",
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
    )
    response.raise_for_status()
    sql_query = response.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    if sql_query.startswith("```sqlite"):
        sql_query = sql_query.replace("```sqlite", "").strip()
    if sql_query.endswith("```"):
        sql_query = sql_query.replace("```", "").strip()
    return sql_query

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
