"""Module containing recipe service implementations."""
from typing import Iterable, List
from uuid import UUID
from fastapi import HTTPException

from mealapi.core.domain.recipe import Recipe
from mealapi.core.repositories.irecipe import IRecipeRepository
from mealapi.infrastructure.dto.recipedto import RecipeDTO
from mealapi.infrastructure.services.irecipe import IRecipeService
from mealapi.infrastructure.services.iuser import IUserService
from mealapi.infrastructure.services.ai_detector import AIDetector
from dependency_injector.wiring import inject, Provide


class RecipeService(IRecipeService):
    """A class representing recipe service."""

    @inject
    def __init__(
        self,
        recipe_repository: IRecipeRepository = Provide["recipe_repository"],
        user_service: IUserService = Provide["user_service"],
        ai_detector: AIDetector = Provide["ai_detector"]
    ) -> None:
        """The initializer of the recipe service.

        Args:
            recipe_repository (IRecipeRepository): The recipe repository.
            user_service (IUserService): The user service.
            ai_detector (AIDetector): The AI detector.
        """
        self.recipe_repository = recipe_repository
        self.user_service = user_service
        self.ai_detector = ai_detector

    async def get_all_recipes(self) -> Iterable[RecipeDTO]:
        """The getting all recipes from the data storage.

        Returns:
            Iterable[RecipeDTO]: All recipes in the data storage.
            
        Raises:
            HTTPException: If there's an error fetching recipes.
        """
        try:
            recipes = await self.recipe_repository.get_all_recipes()
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_by_id(self, recipe_id: int) -> RecipeDTO | None:
        """The getting a recipe from the data storage by id.

        Args:
            recipe_id (int): The id of the recipe.

        Returns:
            RecipeDTO | None: The recipe data if exists.
            
        Raises:
            HTTPException: If recipe not found or there's an error fetching it.
        """
        try:
            recipe = await self.recipe_repository.get_by_id(recipe_id)
            if not recipe:
                raise HTTPException(status_code=404, detail=f"Recipe with id {recipe_id} not found")
            return RecipeDTO.from_record(recipe)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_name(self, recipe_name: str) -> RecipeDTO | None:
        """The getting a recipe from the data storage by name.

        Args:
            recipe_name (str): The name of the recipe.

        Returns:
            RecipeDTO | None: The recipe data if exists.
            
        Raises:
            HTTPException: If no recipes are found with the given name or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_name(recipe_name)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found with given name")
            return RecipeDTO.from_record(recipes[0])
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_category(self, category: str) -> Iterable[RecipeDTO]:
        """Get recipes by category.

        Args:
            category (str): The category to filter by

        Returns:
            Iterable[RecipeDTO]: All recipes in the specified category
            
        Raises:
            HTTPException: If no recipes found in category or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_category(category)
            if not recipes:
                raise HTTPException(status_code=404, detail=f"No recipes found in category '{category}'")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_tag(self, tag: str) -> Iterable[RecipeDTO]:
        """Get recipes by tag.

        Args:
            tag (str): The tag to filter by

        Returns:
            Iterable[RecipeDTO]: All recipes with the specified tag
            
        Raises:
            HTTPException: If no recipes found with tag or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_tag(tag)
            if not recipes:
                raise HTTPException(status_code=404, detail=f"No recipes found with tag '{tag}'")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_preparation_time(self, preparation_time: int) -> Iterable[RecipeDTO]:
        """Get recipes from the data storage by preparation time.

        Args:
            preparation_time (int): The preparation time of the recipes.

        Returns:
            Iterable[RecipeDTO]: The recipes with the given preparation time.
            
        Raises:
            HTTPException: If no recipes found with given preparation time or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_preparation_time(preparation_time)
            if not recipes:
                raise HTTPException(status_code=404, detail=f"No recipes found with preparation time {preparation_time} minutes")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_average_rating(self, average_rating: float) -> Iterable[RecipeDTO]:
        """Get recipes with average rating >= specified value.

        Args:
            average_rating (float): Minimum average rating to filter by

        Returns:
            Iterable[RecipeDTO]: Recipes with average rating >= specified value
            
        Raises:
            HTTPException: If no recipes found with given rating or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_average_rating(average_rating)
            if not recipes:
                raise HTTPException(status_code=404, detail=f"No recipes found with minimum rating {average_rating}")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_ingredients(
        self,
        ingredients: List[str],
        min_match_percentage: float
    ) -> Iterable[RecipeDTO]:
        """Get recipes that can be made with the given ingredients.

        Args:
            ingredients (List[str]): List of ingredients the user has
            min_match_percentage (float): Minimum percentage of recipe ingredients that must be available (0.0 to 1.0)

        Returns:
            Iterable[RecipeDTO]: Recipes that can be made with the given ingredients
            
        Raises:
            HTTPException: If no recipes found with ingredients or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_ingredients(ingredients, min_match_percentage)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found with given ingredients")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_by_user(self, user_id: UUID) -> Iterable[RecipeDTO]:
        """Get all recipes created by a specific user.

        Args:
            user_id (UUID): The ID of the user whose recipes we want to retrieve

        Returns:
            Iterable[RecipeDTO]: All recipes created by the specified user
            
        Raises:
            HTTPException: If no recipes found for user or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_user(user_id)
            if not recipes:
                raise HTTPException(status_code=404, detail=f"No recipes found for user {user_id}")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def get_recipes_by_tag(self, tag: str) -> Iterable[RecipeDTO]:
        """The getting recipes by tag from the data storage.

        Args:
            tag (str): The tag.

        Returns:
            Iterable[RecipeDTO]: The recipe collection.
            
        Raises:
            HTTPException: If no recipes found with tag or there's an error.
        """
        try:
            recipes = await self.recipe_repository.get_by_tag(tag)
            if not recipes:
                raise HTTPException(status_code=404, detail=f"No recipes found with tag '{tag}'")
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def add_recipe(self, recipe: Recipe, user_uuid: UUID) -> RecipeDTO | None:
        """The adding recipe to the data storage.

        Args:
            recipe (Recipe): The recipe data
            user_uuid (UUID): The ID of the user creating the recipe

        Returns:
            RecipeDTO | None: The newly created recipe
            
        Raises:
            HTTPException: If there's an error creating the recipe.
        """
        try:
            # Set the author of the recipe
            recipe_data = await self.recipe_repository.add_recipe(recipe, user_uuid)
            if not recipe_data:
                raise HTTPException(status_code=500, detail="Failed to create recipe")
            return RecipeDTO.from_record(recipe_data)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def update_recipe(self, recipe_id: int, recipe: Recipe, user_uuid: UUID) -> RecipeDTO | None:
        """The updating recipe in the data storage.

        Args:
            recipe_id (int): The recipe id.
            recipe (Recipe): The recipe.
            user_uuid (UUID): The ID of the user attempting to update the recipe.

        Returns:
            RecipeDTO | None: The updated recipe.
            
        Raises:
            HTTPException: If recipe not found, user not authorized, or update fails
        """
        try:
            existing = await self.get_by_id(recipe_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Recipe not found")

            # Check if user is author or admin
            is_author = existing.author == user_uuid
            is_admin = await self.user_service.is_admin(str(user_uuid))

            if not is_author and not is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to update this recipe"
                )

            recipe_data = await self.recipe_repository.update_recipe(recipe_id, recipe)
            if not recipe_data:
                raise HTTPException(status_code=500, detail="Failed to update recipe")
            return RecipeDTO.from_record(recipe_data)
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_recipe(self, recipe_id: int, user_uuid: UUID) -> bool:
        """The deleting recipe from the data storage.

        Args:
            recipe_id (int): The recipe id.
            user_uuid (UUID): The ID of the user attempting to delete the recipe.

        Returns:
            bool: True if recipe was deleted
            
        Raises:
            HTTPException: If recipe not found, user not authorized, or delete fails
        """
        try:
            existing = await self.get_by_id(recipe_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Recipe not found")

            # Check if user is author or admin
            is_author = existing.author == user_uuid
            is_admin = await self.user_service.is_admin(str(user_uuid))

            if not is_author and not is_admin:
                raise HTTPException(
                    status_code=403,
                    detail="Not authorized to delete this recipe"
                )

            deleted = await self.recipe_repository.delete_recipe(recipe_id)
            if not deleted:
                raise HTTPException(status_code=500, detail="Failed to delete recipe")
            return True
        except Exception as e:
            if isinstance(e, HTTPException):
                raise
            raise HTTPException(status_code=500, detail=str(e))
