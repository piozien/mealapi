"""Module containing recipe service abstractions."""

from typing import Iterable, List, Optional
from uuid import UUID
from abc import ABC, abstractmethod
from mealapi.core.domain.recipe import Recipe
from mealapi.infrastructure.dto.recipedto import RecipeDTO

class IRecipeService(ABC):
    """A class representing recipe repository"""

    @abstractmethod
    async def get_all_recipes(self) -> Iterable[RecipeDTO]:
        """The abstract getting all recipes from the data storage.

        Returns:
            Iterable[RecipeDTO]: All recipes in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, recipe_id: int) -> RecipeDTO | None:
        """The abstract getting a recipe from the data storage by id.

        Args:
            recipe_id (int): The id of the recipe.

        Returns:
            RecipeDTO | None: The recipe data if exists.
        """

    @abstractmethod
    async def get_by_name(self, recipe_name: str) -> RecipeDTO | None:
        """The abstract getting a recipe from the data storage by name.

        Args:
            recipe_name (str): The name of the recipe.

        Returns:
            RecipeDTO | None: The recipe data if exists.
        """

    @abstractmethod
    async def get_by_category(self, category: str) -> Iterable[RecipeDTO]:
        """Get recipes by category.

        Args:
            category (str): The category to filter by

        Returns:
            Iterable[RecipeDTO]: All recipes in the specified category
        """

    @abstractmethod
    async def get_by_tag(self, tag: str) -> Iterable[RecipeDTO]:
        """Get recipes by tag.

        Args:
            tag (str): The tag to filter by

        Returns:
            Iterable[RecipeDTO]: All recipes with the specified tag
        """

    @abstractmethod
    async def get_by_preparation_time(self, preparation_time: int) -> Iterable[RecipeDTO]:
        """Get recipes from the data storage by preparation time.

        Args:
            preparation_time (int): The preparation time of the recipes.

        Returns:
            Iterable[RecipeDTO]: The recipes with the given preparation time.
        """

    @abstractmethod
    async def get_by_average_rating(self, average_rating: float) -> Iterable[RecipeDTO]:
        """Get recipes from the data storage by average rating.

        Args:
            average_rating (float): The average rating of the recipes.

        Returns:
            Iterable[RecipeDTO]: The recipes with the given average rating.
        """

    @abstractmethod
    async def get_by_ingredients(
        self,
        ingredients: List[str],
        min_match_percentage: float
    ) -> Iterable[RecipeDTO]:
        """Get recipes that can be made with the given ingredients.

        Args:
            ingredients (List[str]): List of ingredients the user has
            min_match_percentage (float): Minimum percentage of recipe ingredients
                that must be available (0.0 to 1.0)

        Returns:
            Iterable[RecipeDTO]: Recipes that can be made with the given ingredients,
                sorted by match percentage
        """

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> Iterable[RecipeDTO]:
        """Get all recipes created by a specific user.

        Args:
            user_id (UUID4): The ID of the user whose recipes we want to retrieve

        Returns:
            Iterable[RecipeDTO]: All recipes created by the specified user
        """

    @abstractmethod
    async def add_recipe(self, recipe: Recipe) -> RecipeDTO | None:
        """The abstract adding a new recipe to the data storage.

        Args:
            recipe (Recipe): The attributes of the recipe.

        Returns:
            RecipeDTO | None: The newly created recipe.
        """

    @abstractmethod
    async def update_recipe(self, recipe_id: int, recipe: Recipe) -> RecipeDTO | None:
        """The abstract updating recipe data in the data storage.

        Args:
            recipe_id (int): The id of the recipe.
            recipe (Recipe): The attributes of the recipe.

        Returns:
            RecipeDTO | None: The updated recipe.
        """

    @abstractmethod
    async def delete_recipe(self, recipe_id: int) -> bool:
        """The abstract updating removing recipe from the data storage.

        Args:
            recipe_id (int): The id of the recipe.
        """