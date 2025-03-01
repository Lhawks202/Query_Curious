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
1. Clone the repo
2. Download the `northwind.sqlite` binary from releases
3. Place that binary in `<project-root>/northwind/`
4. Run `flask --app northwind init-db` to update the Northwind DB schema

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

#### 3. **Shopping Cart Management**
   - If a user attempts to add more items to the cart than are available in stock, the system will add as many items as possible, while displaying an error message to inform the user that not all requested items could be added. This provides a clear and transparent shopping experience.

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