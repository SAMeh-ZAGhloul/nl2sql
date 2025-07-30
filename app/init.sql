
CREATE TABLE departments (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT
);

CREATE TABLE jobs (
    job_id TEXT PRIMARY KEY,
    job_title TEXT
);

CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    hire_date TEXT,
    job_id TEXT,
    department_id INTEGER,
    salary REAL,
    FOREIGN KEY (job_id) REFERENCES jobs (job_id),
    FOREIGN KEY (department_id) REFERENCES departments (department_id)
);

INSERT INTO departments VALUES (1, 'IT'), (2, 'HR'), (3, 'Sales');
INSERT INTO jobs VALUES ('DEV', 'Developer'), ('MGR', 'Manager');
INSERT INTO employees VALUES
(1, 'Alice', 'Wong', 'alice@corp.com', '2021-01-15', 'DEV', 1, 7500),
(2, 'Bob', 'Smith', 'bob@corp.com', '2022-03-20', 'MGR', 2, 8500);
