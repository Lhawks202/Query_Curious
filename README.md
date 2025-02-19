### Northwind ECommerce Site

## Meet the Team
### Hi there, we are Query Curious! 
Our Team members are:
- Luke Sanford :: Unit Testing
- Joshua Gorniak :: Development Engineer - Shopping Cart and Checkout
- Rafael Singer :: Development Engineer - Authentication
- Katie Baek :: 
- Sofia Utoft ::

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
