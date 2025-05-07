### Northwind ECommerce Site

## Meet the Team
### Hi there, we are Query Curious! 
Our Team members are:
- Luke Sanford :: Unit Testing
- Joshua Gorniak :: Development Engineer - Shopping Cart and Checkout
- Rafael Singer :: Development Engineer - Authentication
- Katie Baek :: Development Engineer - Searching & Product Page
- Sofia Utoft :: Development Engineer - Browsing & Documentation

## Setting up your environment
1. Clone the repository. 
2. Download the `northwind.sqlite` binary from the releases tab in the top-level repository view.
3. Place that binary in `<project-root>/northwind/`
4. Set up a virtual environment:
   a. Run `python -m venv env` to create a virtual environment.
   b. Run `source env/bin/activate` (Mac/Linux) or `env\Scripts\activate` (Windows) to activate the virtual environment.
5. Run `pip install -r requirements` to install all necessary requirements.
6. Run `flask --app northwind init-db` to update the Northwind DB schema.
7.  Run `flask --app northwind run` to start the Flask application.
8. Navigate to the local URL provided in the terminal to access the app.

## Testing
To generate a full interactable testing report on coverage you can view in a web browser:
- Run `pytest --cov=northwind --cov-report=html`
- Look at terminal output to see which tests passed and which failed.
- For information on code coverage and test specifics open `<project-root>/htmlcov/index.html` to see the report.

To generate a quick report on test coverage in your terminal:
- Run `pytest --cov=northwind --cov-report=term`
- You will see the test coverage and results in the terminal.

To test a single file:
- Run `pytest <path/to/testfile.py>` 
- EX: `pytest tests/test_auth.py`

## About

This application is a **three-tier system**:
- **Flask** handles the top (application client) and middle (application server) tiers.
- The **SQLite version of the Northwind database** forms the bottom (database system) tier.

The application includes several essential e-commerce features, including customer account management, product searching, browsing, cart management, and checkout (excluding payment transactions).

### Key Features of the Solution

#### 1. **Logo Home Button**
   - A logo on every page serves as a clickable home button, allowing users to easily return to the homepage for seamless navigation across the website.

#### 2. **Product Search and Browsing by Category**
   - Users can either search for products by name or browse through product categories. After a user chooses whether to browse by category or search, these functionalities are separated to enhance usability and make it easier for users to find what they’re looking for.

#### 3. **Shopping Cart Management and Integration with Checkout**
   - A structured approach to shopping cart functionality ensures an efficient and user-friendly experience. The system includes:
     - **Schemas:** Two schemas, `Shopping_Cart` and `Cart_Items`, allow for efficient storage and reassignment of products when merging guest carts with user accounts.
     - **Session and User Prioritization:** The cart logic prioritizes user sessions and accounts to ensure continuity across browsing sessions.
     - **Flask WTForms Integration:** Used for input validation and enhanced security when updating cart items.

#### 4. **Key Shopping Cart Functionalities**

##### `view_cart()`
   - Displays the shopping cart and provides options to modify item quantities using Flask WTForms.
   - Retrieves cart data based on session ID if the user is not logged in, or user ID if they are logged in.

##### `update_quantity()`
   - Validates whether an item count modification would exceed stock limits.
   - Updates `numItems` and `totalPrice` attributes in the `Shopping_Cart` schema accordingly.
   - Notifies the user if they attempt to exceed stock availability.

##### `remove_item()`
   - Deletes an item from the `Cart_Items` relation.
   - Updates `numItems` and `totalPrice` in the `Shopping_Cart` schema after removal.

##### `add_to_cart()`
   - Integrates product search and browse functionalities with cart management.
   - Creates a new shopping cart if one does not exist for the session/user.
   - Either adds a new item or updates an existing one, ensuring quantities do not exceed stock limits.
   - Updates `numItems` and `totalPrice` accordingly.

##### `assign_user()`
   - Merges a guest’s cart with their logged-in account’s cart upon authentication.
   - If a user cart already exists, items from the session cart are either added or updated before deleting the session cart.

### Testing Methodology

To ensure the robustness and reliability of the system, extensive **unit testing** was performed, covering the following key areas:

- **User Registration and Login**: Validated proper handling of edge cases such as missing or incorrect input during registration and login.
- **Search Functionality**: Tested search capabilities to ensure they handle both valid and invalid inputs correctly.
- **Shopping Cart Management**: Verified that products could be added to the cart and the cart properly updated, including handling stock availability.
- **Boundary Testing**: Tested each method with boundary conditions, such as missing or incorrect input data.
- **Expected Behavior**: Ensured the system functions correctly under normal conditions (e.g., successful searches, adding items to the cart).
- **Security**: Implemented tests to prevent SQL injection attacks and ensure database security.

#### Key Enhancements:
- **Modular Tests**: Tests were split into multiple functions and files to improve error isolation and debugging efficiency.
- **Helper Classes**: Created classes like `CartActions` to avoid code duplication and ensure consistent testing across features.
- **Pytest Fixtures**: Configured `pytest` fixtures in `conftest.py` to pass essential objects directly into test methods.
- **CSRF Token Workaround**: Disabled CSRF tokens during testing due to key mismatches, as bot protection was not the focus of the tests.

This approach ensured a secure, stable, and efficient application, with easy-to-maintain tests and a streamlined debugging process.
