# ER Diagram Documentation

This document explains the design behind the Entity-Relationship (ER) diagram for the Dance Learning System. The system is designed to help users learn, rate, and organize dances through a structured and modular architecture.

---

## Entities & Attributes

### 1. `User`
- Represents individuals using the platform.
- **Attributes:**
  - `ID` (Primary Key)
  - `name`
  - `email`
  - `state`
  - `city`

### 2. `Dance`
- Represents a dance available in the system.
- **Attributes:**
  - `ID` (Primary Key)
  - `vlink`
  - `date`
  - `source

### 3. `Step`
- Represents a single movement or unit of choreography.
- **Attributes:**
  - `ID` (Primary Key)
  - `sequence`

### 4. `Figure`
- Represents a figure illustrating a part of a step.
- **Attributes:**
  - `ID` (Primary Key)
  - `move`

---

## Relationships & Associative Entities

### `Dance_Step`
- Many-to-Many relationship between `Dance` and `Step`.
- Allows a dance to be constructed from multiple steps.
- Many dances have many steps and this participation is total. Every dance must have at least one step, and every step must be assigned to at least one dance.

### `Figure_Step`
- Many-to-One relationship between `Figure` and `Step`.
- Illustrated the movements for one step.
- Every figure must have a coordinating step.
- **Attributes:**
  - `place`
     - Represents the order or position of the figures within a given step.


### `Learning`
- Tracks the dances a user is currently learning.
- Many users can learn many different dances.
- **Attributes:**
  - `date_added`

### `Favorites`
- Allows users to mark dances as favorites.
- Many users can favorite many different dances.
- **Attributes:**
  - `date_added`
  - `rating`

---

## Design Goals

- **Normalization:** Clean separation of concerns for reusability and minimal redundancy.
- **Modularity:** Steps and figures can be reused across multiple dances.
- **Scalability:** Easily supports large numbers of users and dances.
- **User Engagement:** Features like learning status, ratings, and favorites keep users active and invested.
- **Extensibility:** Future features like comments, difficulty tracking, and progress analytics can be easily integrated.

---
