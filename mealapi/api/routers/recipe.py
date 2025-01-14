"""Recipe router module."""

from typing import Optional
from uuid import UUID
from datetime import datetime

from jose import jwt
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mealapi.container import Container
from mealapi.core.domain.recipe import Recipe, RecipeIn
from mealapi.infrastructure.dto.recipedto import RecipeDTO
from mealapi.infrastructure.services.irecipe import IRecipeService
from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM

bearer_scheme = HTTPBearer()

router = APIRouter(
    prefix="/recipes",
    tags=["recipes"],
)


@router.get("/", response_model=list[RecipeDTO])
@inject
async def get_recipes(
        id: Optional[int] = Query(None, description="Recipe ID"),
        name: Optional[str] = Query(None, description="Recipe name (partial match)"),
        ingredients: Optional[str] = Query(None, description="Comma-separated list of ingredients"),
        min_match_percentage: Optional[float] = Query(None, ge=0.0, le=1.0,
                                                      description="Minimum percentage of matching ingredients (if not"
                                                                  " specified, requires exact match)"),
        preparation_time: Optional[int] = Query(None, gt=0, description="Preparation time in minutes"),
        min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum average rating"),
        category: Optional[str] = Query(None, description="Recipe category"),
        author_id: Optional[UUID] = Query(None, description="Author's UUID"),
        tag: Optional[str] = Query(None, description="Recipe tag"),
        service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes with optional filtering.
    
    You can filter recipes by various criteria. All filters are optional and can be combined.
    If no filters are provided, returns all recipes.

    Args:
        id: Filter by recipe ID
        name: Filter by recipe name (partial match)
        ingredients: Filter by required ingredients (comma-separated)
        min_match_percentage: Minimum percentage of ingredients that must match (0.0 to 1.0)
        preparation_time: Filter by exact preparation time in minutes
        min_rating: Filter by minimum average rating (0 to 5)
        category: Filter by recipe category
        author_id: Filter by recipe author's UUID
        tag: Filter by recipe tag
        service: The recipe service (injected)

    Returns:
        List of matching recipes

    Raises:
        HTTPException: If no recipes found or if validation fails
    """
    try:
        if id is not None:
            recipe = await service.get_by_id(id)
            return [recipe] if recipe else []

        if ingredients:
            if min_match_percentage is None:
                raise HTTPException(
                    status_code=400,
                    detail="min_match_percentage is required when filtering by ingredients"
                )

            ingredient_list = [i.strip() for i in ingredients.split(",")]
            recipes = await service.get_by_ingredients(ingredient_list, min_match_percentage)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found with given ingredients")
            return recipes

        if name:
            recipe = await service.get_by_name(name)
            if not recipe:
                raise HTTPException(status_code=404, detail="No recipes found with given name")
            return [recipe]

        if preparation_time:
            recipes = await service.get_by_preparation_time(preparation_time)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found with given preparation time")
            return recipes

        if min_rating is not None:
            recipes = await service.get_by_average_rating(min_rating)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found with given minimum rating")
            return recipes

        if category:
            recipes = await service.get_by_category(category)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found in given category")
            return recipes

        if author_id:
            recipes = await service.get_by_user(author_id)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found for given author")
            return recipes

        if tag:
            recipes = await service.get_by_tag(tag)
            if not recipes:
                raise HTTPException(status_code=404, detail="No recipes found with given tag")
            return recipes

        # If no filters specified, return all recipes
        return await service.get_all_recipes()

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.get("/all", response_model=list[RecipeDTO])
@inject
async def get_all_recipes(
        service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get all recipes.

    Args:
        service: The recipe service (injected)

    Returns:
        List of all recipes

    Raises:
        HTTPException: If no recipes found
    """
    try:
        recipes = await service.get_all_recipes()
        if not recipes:
            raise HTTPException(
                status_code=404,
                detail="Not found: No recipes exist in the system"
            )
        return recipes

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.post("/", response_model=RecipeDTO, status_code=201)
@inject
async def create_recipe(
        recipe: RecipeIn,
        service: IRecipeService = Depends(Provide[Container.recipe_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> RecipeDTO:
    """Create a new recipe.

    Required fields:
        - name: Recipe name
        - instructions: Cooking instructions
        - ingredients: List of "amount:ingredient" (e.g. ["2 cups:flour", "1:egg"])
        - preparation_time: Time in minutes
        - category: e.g. "Dessert", "Main Course"

    Optional fields:
        - description: Short description
        - servings: Number of servings
        - difficulty: "easy", "medium", or "hard"
        - steps: List of step-by-step instructions
        - tags: List of searchable tags

    Args:
        recipe: Recipe data
        service: The recipe service (injected)
        credentials: User credentials

    Returns:
        Created recipe with generated ID

    Raises:
        HTTPException: If unauthorized or invalid input
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        # Convert RecipeIn to Recipe domain model
        recipe_domain = Recipe(
            name=recipe.name,
            description=recipe.description,
            instructions=recipe.instructions,
            ingredients=recipe.ingredients,
            preparation_time=recipe.preparation_time,
            servings=recipe.servings,
            difficulty=recipe.difficulty,
            category=recipe.category,
            tags=recipe.tags,
            steps=recipe.steps,
            author=UUID(user_uuid),  # Set the author field
            created_at=datetime.now()  # Set creation time
        )

        new_recipe = await service.add_recipe(recipe_domain, UUID(user_uuid))
        if not new_recipe:
            raise HTTPException(
                status_code=500,
                detail="Server error: Failed to create recipe"
            )
        return new_recipe

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.put("/{recipe_id}", response_model=RecipeDTO)
@inject
async def update_recipe(
        recipe_id: int,
        updated_recipe: RecipeIn,
        service: IRecipeService = Depends(Provide[Container.recipe_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> RecipeDTO:
    """Update an existing recipe.

    Only the recipe author or an admin can update the recipe.

    Args:
        recipe_id: ID of the recipe to update
        updated_recipe: New recipe data
        service: The recipe service (injected)
        credentials: User credentials

    Returns:
        Updated recipe

    Raises:
        HTTPException: If recipe not found, unauthorized, or invalid input
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        recipe = await service.update_recipe(recipe_id, updated_recipe, UUID(user_uuid))
        if not recipe:
            raise HTTPException(
                status_code=404,
                detail=f"Not found: Recipe with ID {recipe_id} does not exist"
            )
        return recipe

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.delete("/{recipe_id}", status_code=204)
@inject
async def delete_recipe(
        recipe_id: int,
        service: IRecipeService = Depends(Provide[Container.recipe_service]),
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> None:
    """Delete a recipe.

    Only the recipe author or an admin can delete the recipe.

    Args:
        recipe_id: ID of the recipe to delete
        service: The recipe service (injected)
        credentials: User credentials

    Raises:
        HTTPException: If recipe not found or unauthorized
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Authentication failed: Invalid or missing user ID in token"
            )

        if not await service.delete_recipe(recipe_id, UUID(user_uuid)):
            raise HTTPException(
                status_code=404,
                detail=f"Not found: Recipe with ID {recipe_id} does not exist"
            )

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Authentication failed: Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )
