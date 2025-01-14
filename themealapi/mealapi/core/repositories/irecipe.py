"""Module containing recipe repository abstractions.

This module defines the interface for recipe repositories, specifying
the contract that any recipe repository implementation must fulfill.
The interface provides methods for managing recipes in the data storage,
including CRUD operations and various query methods.
"""

from abc import ABC, abstractmethod
from typing import Any, Iterable, List
from uuid import UUID

from mealapi.core.domain.recipe import Recipe, RecipeIn


class IRecipeRepository(ABC):
    """Abstract base class defining the recipe repository interface.
    
    This interface defines all operations that must be supported by
    any concrete recipe repository implementation. It provides methods
    for retrieving, creating, updating, and deleting recipes, as well
    as various query methods for searching and filtering recipes.
    """

    @abstractmethod
    async def get_all_recipes(self) -> Iterable[Any]:
        """Retrieve all recipes from the data storage.

        Returns:
            Iterable[Any]: Collection of all recipes in the system

        Note:
            The returned recipes should include basic metadata but may
            not include full details like comments and ratings for
            performance reasons.
        """

    @abstractmethod
    async def get_by_id(self, recipe_id: int) -> Any | None:
        """Retrieve a recipe by its ID.

        Args:
            recipe_id (int): ID of the recipe to retrieve

        Returns:
            Any | None: The recipe data if found, None otherwise

        Note:
            The returned recipe should include all related data including
            comments, ratings, and author information.
        """

    @abstractmethod
    async def get_by_name(self, recipe_name: str) -> Any | None:
        """Retrieve a recipe by its name.

        Args:
            recipe_name (str): Name of the recipe to retrieve

        Returns:
            Any | None: The recipe data if found, None otherwise

        Note:
            The search should be case-insensitive and may include
            partial matches based on implementation.
        """

    @abstractmethod
    async def get_by_preparation_time(self, preparation_time: int) -> Iterable[Any]:
        """Retrieve recipes by preparation time.

        Args:
            preparation_time (int): Maximum preparation time in minutes

        Returns:
            Iterable[Any]: Collection of recipes within the time limit

        Note:
            Returns recipes that can be prepared in less than or equal
            to the specified time.
        """

    @abstractmethod
    async def get_by_category(self, category: str) -> Iterable[Any]:
        """Retrieve recipes by category.

        Args:
            category (str): Category to filter by

        Returns:
            Iterable[Any]: Collection of recipes in the category

        Note:
            Categories should be standardized and case-insensitive.
        """

    @abstractmethod
    async def get_by_author(self, author_id: UUID) -> Iterable[Any]:
        """Retrieve recipes by author.

        Args:
            author_id (UUID): ID of the recipe author

        Returns:
            Iterable[Any]: Collection of recipes by the author

        Note:
            Results should be ordered by creation date, with the
            most recent recipes first.
        """

    @abstractmethod
    async def add_recipe(self, recipe: RecipeIn) -> Any:
        """Create a new recipe.

        Args:
            recipe (RecipeIn): Recipe data to create

        Returns:
            Any: The created recipe with generated ID and metadata

        Note:
            The method should handle setting the creation timestamp
            and validating all required fields.
        """

    @abstractmethod
    async def update_recipe(self, recipe_id: int, recipe: RecipeIn) -> Any:
        """Update an existing recipe.

        Args:
            recipe_id (int): ID of the recipe to update
            recipe (RecipeIn): New recipe data

        Returns:
            Any: The updated recipe data

        Note:
            Only the recipe content and metadata should be updatable.
            Author and creation date should remain unchanged.
        """

    @abstractmethod
    async def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe.

        Args:
            recipe_id (int): ID of the recipe to delete

        Returns:
            bool: True if recipe was deleted, False if not found

        Note:
            This operation should also handle cleanup of all related
            data such as comments, ratings, and reports.
        """

    @abstractmethod
    async def search_recipes(self, query: str) -> Iterable[Any]:
        """Search recipes by query string.

        Args:
            query (str): Search query string

        Returns:
            Iterable[Any]: Collection of matching recipes

        Note:
            The search should look for matches in recipe names,
            descriptions, ingredients, and other relevant fields.
            Results should be ordered by relevance.
        """