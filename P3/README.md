# English Country Dancing

This document explains the design of the English Country Dancing Flask App. The system is designed to help users learn, rate, and organize dances through a structured and modular architecture.

---
## Meet the Team
### Hi there, we are Query Curious! 
Our Team members are:
- Luke Sanford :: Unit Testing
- Joshua Gorniak :: Development Engineer - 
- Rafael Singer :: Development Engineer - 
- Katie Baek :: Development Engineer - 
- Sofia Utoft :: Development Engineer - Authentication & Initialization


## ER Diagram
### Entities & Attributes

#### 1. `User`
- Represents individuals using the platform.
- **Attributes:**
  - `ID` (Primary Key)
  - `name`
  - `email`
  - `state`
  - `city`

#### 2. `Dance`
- Represents a dance available in the system.
- **Attributes:**
  - `ID` (Primary Key)
  - `dance_name`
  - `video`
  - `source

### 3. `Step`
- Represents a single movement or unit of choreography.
- **Attributes:**
  - `ID` (Primary Key)
  - `step_name`

#### 4. `Figure`
- Represents a figure illustrating a part of a step.
- **Attributes:**
  - `ID` (Primary Key)
  - `name`
  - `role`
  - `start_position`
  - `action`
  - `end_position`
  - `duration`

---

### Relationships & Associative Entities

#### `Dance_Step`
- Many-to-Many relationship between `Dance` and `Step`.
- Allows a dance to be constructed from multiple steps.
- Many dances have many steps and this participation is total. Every dance must have at least one step, and every step must be assigned to at least one dance.

#### `Figure_Step`
- Many-to-One relationship between `Figure` and `Step`.
- Illustrated the movements for one step.
- Every figure must have a coordinating step.
- **Attributes:**
  - `place`
     - Represents the order or position of the figures within a given step.


#### `Learning`
- Tracks the dances a user is currently learning.
- Many users can learn many different dances.
- **Attributes:**
  - `date_added`

#### `Learned`
- Allows users to save dances they learned.
- Many users can learn many different dances.
- **Attributes:**
  - `date_added`
  - `rating`

---

### Design Goals

- **Normalization:** Clean separation of concerns for reusability and minimal redundancy.
- **Modularity:** Steps and figures can be reused across multiple dances.
- **Scalability:** Easily supports large numbers of users and dances.
- **User Engagement:** Features like learning status, ratings, and favorites keep users active and invested.
- **Extensibility:** Future features like comments, difficulty tracking, and progress analytics can be easily integrated.

---

## Setting up your environment
1. Clone the repository. 
2. Copy output.zip from P2 directory into root of P3 directory.
3. Unzip output.zip file.
4. Set up a virtual environment:
   a. Run `python -m venv env` to create a virtual environment.
   b. Run `source env/bin/activate` (Mac/Linux) or `env\Scripts\activate` (Windows) to activate the virtual environment.
5. Run `pip install -r requirements.txt` to install all necessary requirements.
6. Run `flask --app dances init-db` to initialize the Dances DB schema.
  a. To populate the database add the `--populate` flag
  b. To delete the database and reinitialize add the `--force` flag
  c. To delete and repopulate add both flags
7.  Run `flask --app dances run` to start the Flask application.
8. Navigate to the local URL provided in the terminal to access the app.