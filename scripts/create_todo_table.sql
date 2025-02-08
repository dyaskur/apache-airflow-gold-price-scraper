CREATE TABLE IF NOT EXISTS todos (
    id INT PRIMARY KEY,
    userId INT,
    title TEXT,
    completed BOOLEAN
);
