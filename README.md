# MealAPI

A recipe management API built with modern Python technologies.

## Technologies Used

- FastAPI 
- SQLAlchemy
- PostgreSQL
- Pydantic 
- JWT 
- Dependency Injector 

## Core Functionalities

### User Management
- User registration and authentication
- Role-based access control (USER, ADMIN)
- JWT token-based authentication

### Recipes
- Create, read, update, and delete recipes
- Search recipes by name or ingredients
- Filter recipes by category
- Rate recipes (1-5 stars)

### Comments
- Add comments to recipes
- Include ratings with comments
- Edit and delete own comments
- Report inappropriate comments

### Admin Features
- Manage reported comments
- View all reports
- Update report status
- Delete inappropriate content

## Test Data

### Registered Users

    email: admin; password: admin123; role: ADMIN; UUID: 123e4567-e89b-12d3-a456-426614174000

```json
        {
            "email": "admin",
            "password": "admin123",
            "role": "ADMIN"
        }
```
    email: user1; password: admin123; role: USER; UUID: 123e4567-e89b-12d3-a456-426614174001
```json
        {
            "email": "user1",
            "password": "admin123",
            "role": "USER"
        }
``` 
    email: user2; password: admin123; role: USER; UUID: 123e4567-e89b-12d3-a456-426614174002
```json
        {
            "email": "user2",
            "password": "admin123",
            "role": "USER"
        }

```

### Sample Recipe
```json
    {
    "name": "Pancakes with maple syrup",
    "description": "A simple and quick recipe for delicious American pancakes with maple syrup.",
    "instructions": "1. In a large bowl, mix the flour, sugar, baking powder and salt. 2. In a second bowl, whisk the eggs with the milk and melted butter. 3. Combine the wet ingredients with the dry ingredients, stirring until you have a smooth batter. 4. Heat a skillet with a little oil over medium heat. 5. Pour portions of the batter into the pan and fry on both sides until golden.6. Serve with maple syrup and your favorite toppings.",
    "category": "breakfast",
    "ingredients": [
        "200g:wheat flour",
        "2 spoons:sugar",
        "1 teaspoon:baking powder",
        "pinch:salt",
        "2:pieces of egg",
        "250ml:milk",
        "50g:butter melted",
        "for frying:oil",
        "to serve:maple syrup"
    ],
    "preparation_time": 20,
    "servings": 4,
    "difficulty": "easy",
    "steps": [
        "In a large bowl, mix flour, sugar, baking powder, and salt.",
        "In another bowl, whisk the eggs with milk and melted butter.",
        "Combine the wet ingredients with the dry ones, stirring until a smooth batter forms.",
        "Heat a pan with a bit of oil over medium heat.",
        "Pour portions of the batter onto the pan and cook on both sides until golden.",
        "Serve with maple syrup and your favorite toppings."
    ],
    "tags": [
        "breakfast",
        "pancakes",
        "quick"
    ]
    }
```

### Sample Comment
    With rating:
```json
    {
        "content": "Good",
        "recipe_id": 4,
        "rating": {
            "value": 4
        }
    }
```
    Without rating:
```json
    {
        "content": "Good",
        "recipe_id": 4,
        "rating": {
            "value": null
        }
    }
```
