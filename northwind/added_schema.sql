CREATE TABLE IF NOT EXISTS Authentication (
    UserID TEXT PRIMARY KEY,
    Password TEXT,
    SessionID TEXT,
    FOREIGN KEY (UserID) REFERENCES Customer (Id)
)

CREATE INDEX IF NOT EXISTS idx_product_name ON Product(ProductName);


