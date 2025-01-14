"""Module containing recipe mapping utilities."""

from typing import List, Optional
import re
from datetime import datetime
import unicodedata
from datetime import timezone
from mealapi.core.domain.recipe import Recipe
from mealapi.core.domain.comment import CommentIn


class RecipeMapper:
    """A class for mapping recipe data between different formats."""

    @staticmethod
    def normalize_string(s: str) -> str:
        """Normalize string by removing diacritics and converting to lowercase.

        Args:
            s (str): Input string to normalize

        Returns:
            str: Normalized string
        """
        return ''.join(
            char for char in unicodedata.normalize('NFKD', s.lower())
            if unicodedata.category(char) != 'Mn'
        )

    @staticmethod
    def ingredients_to_strings(ingredients: List[str]) -> List[str]:
        """Convert ingredients to list of strings for database storage.
        
        Args:
            ingredients (List[str]): List of ingredients to convert
            
        Returns:
            List[str]: List of ingredients in string format
        """
        return [
            ing.lower() for ing in ingredients
        ]

    @staticmethod
    def validate_preparation_time(preparation_time: int) -> None:
        """Validate preparation time value.

        Args:
            preparation_time (int): Time in minutes

        Raises:
            ValueError: If preparation time is not positive
        """
        if not isinstance(preparation_time, int):
            raise ValueError("Preparation time must be an integer")
        if preparation_time <= 0:
            raise ValueError("Preparation time must be positive")
        if preparation_time > 1440:
            raise ValueError("Preparation time cannot exceed 24 hours")

    @staticmethod
    def validate_servings(servings: Optional[int]) -> None:
        """Validate servings value.

        Args:
            servings (Optional[int]): Number of servings

        Raises:
            ValueError: If servings is not positive or not an integer
        """
        if servings is None:
            return

        if not isinstance(servings, int):
            raise ValueError("Servings must be an integer")

        if servings <= 0:
            raise ValueError("Servings must be positive")

        if servings > 100:  # Reasonable maximum number of servings
            raise ValueError("Servings cannot exceed 100")

    @staticmethod
    def validate_difficulty(difficulty: Optional[str]) -> None:
        """Validate difficulty level.

        Args:
            difficulty (Optional[str]): Difficulty of the recipe

        Raises:
            ValueError: If difficulty is not one of the allowed values
        """
        if difficulty is None:
            return

        allowed_difficulties = {"easy", "medium", "hard","łatwy","średni","trudny"}
        difficulty_lower = difficulty.lower()

        if difficulty_lower not in allowed_difficulties:
            raise ValueError(f"Difficulty must be one of: {', '.join(allowed_difficulties)}")

    @staticmethod
    def validate_name(name: str) -> None:
        """Validate recipe name.

        Args:
            name (str): Name of the recipe

        Raises:
            ValueError: If name is invalid
        """
        if not name:
            raise ValueError("Recipe name cannot be empty")

        if len(name) > 200:
            raise ValueError("Recipe name cannot exceed 200 characters")

        if not re.match(r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ0-9\s\-\']+$', name):
            raise ValueError("Recipe name contains invalid characters")

    @staticmethod
    def validate_ingredients(ingredients: List[str]) -> None:
        """Validate list of ingredients.

        Args:
            ingredients (List[str]): List of ingredients

        Raises:
            ValueError: If ingredients list is invalid
        """
        if not ingredients:
            raise ValueError("At least one ingredient is required")

        for ingredient in ingredients:
            if not ingredient:
                raise ValueError("Ingredient cannot be an empty string")

            if len(ingredient) > 200:
                raise ValueError("Ingredient name cannot exceed 200 characters")

            # Optional: Check ingredient format (e.g., "amount:ingredient")
            if ':' in ingredient:
                parts = ingredient.split(':', 1)
                if not parts[0] or not parts[1]:
                    raise ValueError(f"Invalid ingredient format: {ingredient}")

    @staticmethod
    def normalize_ingredient(s: str) -> str:
        """Normalize ingredient string by standardizing format and removing noise.

        Args:
            s (str): Input ingredient string to normalize

        Returns:
            str: Normalized ingredient string
        """

        s = RecipeMapper.normalize_string(s)
        
        units = [
            r'\d+(\.\d+)?', 
            # English units
            r'cup(s)?',
            r'tablespoon(s)?', r'tbsp',
            r'teaspoon(s)?', r'tsp',
            r'gram(s)?', r'g',
            r'kilogram(s)?', r'kg',
            r'pound(s)?', r'lb(s)?',
            r'ounce(s)?', r'oz',
            r'milliliter(s)?', r'ml',
            r'liter(s)?', r'l',
            r'pinch(es)?',
            r'handful(s)?',
            r'piece(s)?',
            r'slice(s)?',
            r'to taste',
            r'optional',
            # Polish units
            r'szklank[aię]',
            r'łyżk[aię]', r'łyżeczk[aię]',
            r'gram(y|ów)?',
            r'kilogram(y|ów)?', 
            r'dek[ai]',
            r'dag',
            r'mililitr(y|ów)?',
            r'litr(y|ów)?',
            r'szczypt[aię]',
            r'garść',
            r'sztuk[aię]',
            r'plaster(ek|ki|ków)?',
            r'do smaku',
            r'opcjonalnie',
            r'według uznania',
            r'wedle uznania'
        ]
        
        pattern = '|'.join(fr'\b{unit}\b' for unit in units)
        s = re.sub(pattern, '', s, flags=re.IGNORECASE)
        
        cooking_words = [
            # English words
            r'fresh',
            r'frozen',
            r'dried',
            r'chopped',
            r'diced',
            r'minced',
            r'sliced',
            r'grated',
            r'ground',
            r'whole',
            r'raw',
            r'cooked',
            # Polish words
            r'śwież[aey]',
            r'mrożon[aey]',
            r'suszon[aey]',
            r'posiekan[aey]',
            r'pokrojon[aey]',
            r'zmielon[aey]',
            r'start[aey]',
            r'całe',
            r'surowe',
            r'ugotowan[aey]',
            r'drobno',
            r'grubo',
            r'średnio',
            r'w kostkę',
            r'w plastry',
            r'w plasterki',
            r'w paski'
        ]
        
        pattern = '|'.join(fr'\b{word}\b' for word in cooking_words)
        s = re.sub(pattern, '', s, flags=re.IGNORECASE)
        
        # Clean up whitespace and punctuation
        s = re.sub(r'[,.]', '', s)
        s = re.sub(r'\s+', ' ', s)
        return s.strip()

    @staticmethod
    def validate_created_at(created_at: datetime) -> None:
        """Validate created_at to ensure it is timezone-naive.

        Args:
            created_at (datetime): Datetime to validate

        Raises:
            ValueError: If created_at is not timezone-naive
        """
        if created_at.tzinfo is not None:
            raise ValueError("created_at must be timezone-naive")


    @staticmethod
    def validate_instructions(instructions: str) -> None:
        """Validate recipe instructions.

        Args:
            instructions (str): Cooking instructions

        Raises:
            ValueError: If instructions are invalid
        """
        if not instructions:
            raise ValueError("Instructions cannot be empty")

        if len(instructions) > 2000:
            raise ValueError("Instructions cannot exceed 2000 characters")

    @staticmethod
    def validate_category(category: str) -> None:
        """Validate recipe category.

        Args:
            category (str): Recipe category

        Raises:
            ValueError: If category is invalid
        """
        if not category:
            raise ValueError("Category cannot be empty")

        if len(category) > 100:
            raise ValueError("Category name cannot exceed 100 characters")

        # Optional: Add predefined categories or validation
        allowed_categories = {
            "breakfast", "lunch", "dinner", "dessert", "appetizer",
            "main course", "side dish", "salad", "soup", "beverage"
        }
        category_lower = category.lower()

        # Soft validation - warn if not in predefined categories
        if category_lower not in allowed_categories:
            print(f"Warning: Category '{category}' is not in predefined list")

    @staticmethod
    def validate_tags(tags: Optional[List[str]]) -> None:
        """Validate recipe tags.

        Args:
            tags (Optional[List[str]]): List of tags

        Raises:
            ValueError: If tags are invalid
        """
        if tags is None:
            return

        if not isinstance(tags, list):
            raise ValueError("Tags must be a list")

        for tag in tags:
            if not tag:
                raise ValueError("Tag cannot be an empty string")

            if len(tag) > 50:
                raise ValueError("Tag cannot exceed 50 characters")

            # Optional: Validate tag characters
            if not re.match(r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ0-9\-]+$', tag):
                raise ValueError(f"Invalid tag format: {tag}")

    @staticmethod
    def validate_comment(comment: CommentIn) -> None:
        """Validate comment data.

        Args:
            comment (CommentIn): Comment to validate

        Raises:
            ValueError: If comment data is invalid
        """
        # Validate recipe_id
        if comment.recipe_id is None or comment.recipe_id <= 0:
            raise ValueError("Invalid recipe_id")

        # Validate content
        if not comment.content or len(comment.content.strip()) == 0:
            raise ValueError("Comment content cannot be empty")

        # Validate rating if provided
        if comment.rating is not None:
            if not isinstance(comment.rating, int):
                raise ValueError("Rating must be an integer")
            if comment.rating < 1 or comment.rating > 5:
                raise ValueError("Rating must be between 1 and 5")

    @staticmethod
    def convert_to_utc(dt: Optional[datetime] = None) -> datetime:
        """Convert input datetime or current time to UTC, making it timezone-naive.

        Args:
            dt (Optional[datetime], optional): Input datetime. Defaults to None.

        Returns:
            datetime: Timezone-naive UTC datetime
        """
        if dt is None:
            dt = datetime.now(timezone.utc)
        
        if dt.tzinfo is None:
            return dt
        
        # Convert to UTC and strip timezone information
        return dt.astimezone(timezone.utc).replace(tzinfo=None)


    @classmethod
    def validate(cls, recipe: Recipe) -> None:
        """
        Validate entire recipe object.

        Args:
            recipe (Recipe): Recipe to validate

        Raises:
            ValueError: If any recipe attribute is invalid
        """
        # Validate specific attributes
        cls.validate_preparation_time(recipe.preparation_time)
        
        if recipe.servings is not None:
            cls.validate_servings(recipe.servings)
        
        if recipe.difficulty is not None:
            cls.validate_difficulty(recipe.difficulty)
        
        # Validate name
        if not recipe.name or len(recipe.name.strip()) == 0:
            raise ValueError("Recipe name cannot be empty")
        cls.validate_name(recipe.name)
        
        # Validate instructions
        if not recipe.instructions or len(recipe.instructions.strip()) == 0:
            raise ValueError("Recipe instructions cannot be empty")
        
        # Validate category
        if not recipe.category or len(recipe.category.strip()) == 0:
            raise ValueError("Recipe category cannot be empty")
        
        # Validate ingredients
        if not recipe.ingredients or len(recipe.ingredients) == 0:
            raise ValueError("Recipe must have at least one ingredient")
        
        # Optional additional validations
        if recipe.tags and len(recipe.tags) > 10:
            raise ValueError("Maximum of 10 tags allowed")
        
        if recipe.steps and len(recipe.steps) > 20:
            raise ValueError("Maximum of 20 steps allowed")
