"""Module containing recipe repository abstractions."""

from abc import ABC, abstractmethod
from typing import Any, Iterable, List
from uuid import UUID

from mealapi.core.domain.recipe import Recipe


class IRecipeRepository(ABC):
    """An abstract class representing protocol of recipe repository."""

    @abstractmethod
    async def get_all_recipes(self) -> Iterable[Any]:
        """The abstract getting all recipes from the data storage.

        Returns:
            Iterable[Any]: All recipes in the data storage.
        """

    @abstractmethod
    async def get_by_id(self, recipe_id: int) -> Any | None:
        """The abstract getting a recipe from the data storage by id.

        Args:
            recipe_id (int): The id of the recipe.

        Returns:
            Any | None: The recipe data if exists.
        """

    @abstractmethod
    async def get_by_name(self, recipe_name: str) -> Any | None:
        """The abstract getting a recipe from the data storage by name.

        Args:
            recipe_name (str): The name of the recipe.

        Returns:
            Any | None: The recipe data if exists.
        """

    @abstractmethod
    async def get_by_preparation_time(self, preparation_time: int) -> Iterable[Any]:
        """The abstract getting recipes from the data storage by preparation time.

        Args:
            preparation_time (int): The preparation time of the recipes.

        Returns:
            Iterable[Any]: The recipes with the given preparation time.
        """

    @abstractmethod
    async def get_by_average_rating(self, average_rating: float) -> Iterable[Any]:
        """The abstract getting recipes from the data storage by average rating.

        Args:
            average_rating (float): The average rating of the recipes.

        Returns:
            Iterable[Any]: The recipes with the given average rating.
        """

    @abstractmethod
    async def get_by_ingredients(self, ingredients: List[str], min_match_percentage: float) -> Iterable[Any]:
        """Get recipes that can be made with the given ingredients.

        Args:
            ingredients (List[str]): List of ingredients the user has
            min_match_percentage (float): Minimum percentage of recipe ingredients that must be available (0.0 to 1.0)

        Returns:
            Iterable[Any]: Recipes that can be made with the given ingredients, sorted by match percentage
        """

    @abstractmethod
    async def get_by_user(self, user_id: UUID) -> Iterable[Any]:
        """Get all recipes created by a specific user.

        Args:
            user_id (UUID): The ID of the user whose recipes we want to retrieve

        Returns:
            Iterable[Any]: All recipes created by the specified user
        """

    @abstractmethod
    async def get_by_category(self, category: str) -> Iterable[Any]:
        """Get recipes by category.

        Args:
            category (str): The category to filter by

        Returns:
            Iterable[Any]: All recipes in the specified category
        """

    @abstractmethod
    async def get_by_tag(self, tag: str) -> Iterable[Any]:
        """Get recipes by tag.

        Args:
            tag (str): The tag to filter by

        Returns:
            Iterable[Any]: All recipes with the specified tag
        """

    @abstractmethod
    async def add_recipe(self, recipe: Recipe, author: UUID) -> Any | None:
        """The abstract adding a new recipe to the data storage.

        Args:
            recipe (Recipe): The attributes of the recipe.
            author (UUID): The author of the recipe.

        Returns:
            Any | None: The newly created recipe.
        """

    @abstractmethod
    async def update_recipe(self, recipe_id: int, recipe: Recipe) -> Any | None:
        """The abstract updating recipe data in the data storage.

        Args:
            recipe_id (int): The id of the recipe.
            recipe (Recipe): The attributes of the recipe.

        Returns:
            Any | None: The updated recipe.
        """

    @abstractmethod
    async def delete_recipe(self, recipe_id: int) -> bool:
        """The abstract updating removing recipe from the data storage.

        Args:
            recipe_id (int): The id of the recipe.
        """