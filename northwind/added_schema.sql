CREATE TABLE IF NOT EXISTS Authentication (
    UserID TEXT PRIMARY KEY,
    Password TEXT,
    SessionID TEXT,
    FOREIGN KEY (UserID) REFERENCES Customer (Id)
)