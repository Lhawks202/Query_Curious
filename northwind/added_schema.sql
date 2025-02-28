CREATE TABLE IF NOT EXISTS Authentication (
    UserID TEXT PRIMARY KEY,
    Password TEXT,
    SessionID TEXT,
    FOREIGN KEY (UserID) REFERENCES Customer (Id)
);

CREATE INDEX IF NOT EXISTS idx_product_name ON Product(ProductName);

CREATE TABLE IF NOT EXISTS Shopping_Cart (
    CartID INTEGER PRIMARY KEY AUTOINCREMENT,
    SessionID TEXT NOT NULL,
    UserID TEXT, -- Nullable; will be updated once the user logs in
    NumItems INTEGER DEFAULT 0,
    TotalCost REAL DEFAULT 0.0,
    CreatedTimestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastUpdated DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Authentication(UserID)
);

CREATE TABLE IF NOT EXISTS Cart_Items (
    CartItemID INTEGER PRIMARY KEY AUTOINCREMENT,
    CartID INTEGER,
    OrderID INTEGER,
    ProductID INTEGER NOT NULL,
    Quantity INTEGER NOT NULL DEFAULT 1,
    AddedTimestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CartID) REFERENCES Shopping_Cart(CartID),
    FOREIGN KEY (ProductID) REFERENCES Product(Id)
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
    CHECK (OrderID IS NOT NULL OR CartID IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS Orders (
    OrderID INTEGER PRIMARY KEY AUTOINCREMENT,
    UserID TEXT NOT NULL,
    TotalCost REAL NOT NULL,
    NumItems INTEGER NOT NULL,
    CreatedTimestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Authentication(UserID)
);
