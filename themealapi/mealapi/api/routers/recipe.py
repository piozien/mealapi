"""A module containing recipe endpoints."""

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from uuid import UUID

from mealapi.infrastructure.utils.consts import SECRET_KEY, ALGORITHM
from mealapi.container import Container
from mealapi.core.domain.recipe import RecipeIn, Recipe
from mealapi.infrastructure.dto.recipedto import RecipeDTO
from mealapi.infrastructure.services.irecipe import IRecipeService
from mealapi.infrastructure.services.iuser import IUserService
from mealapi.core.domain.user import UserRole

bearer_scheme = HTTPBearer()
router = APIRouter(
    tags=["recipe"]
)


async def is_admin(user_uuid: str, user_service: IUserService) -> bool:
    """Check if the user has admin role.

    Args:
        user_uuid (str): The UUID of the user to check
        user_service (IUserService): The user service instance

    Returns:
        bool: True if user is admin, False otherwise
    """
    user = await user_service.get_by_uuid(UUID(user_uuid))
    return user is not None and user.role == UserRole.ADMIN


@router.get("/get-all", response_model=list[RecipeDTO])
@inject
async def get_all_recipes(
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get all recipes.

    Returns:
        list[RecipeDTO]: List of all recipes with their details.

    Example response:
        [
            {
                "id": 1,
                "name": "Spaghetti Carbonara",
                "description": "Classic Italian pasta dish",
                "instructions": "Step by step instructions...",
                "category": "Main Course",
                "ingredients": ["200g:pasta", "100g:pancetta"],
                "preparation_time": 30,
                "servings": 4,
                "difficulty": "medium",
                "author": "123e4567-e89b-12d3-a456-426614174000",
                "created_at": "2025-01-04T19:20:30.123Z",
                "average_rating": 4.5,
                "ai_detected": 0.12
            }
        ]
    """
    return await service.get_all_recipes()


@router.get("/recipes/by-ingredients", response_model=list[RecipeDTO])
@inject
async def get_recipes_by_ingredients(
    ingredients: str,
    min_match_percentage: float = 0.5,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Find recipes that can be made with given ingredients.

    Args:
        ingredients (str): Comma-separated list of ingredients
        min_match_percentage (float, optional): Minimum percentage of recipe ingredients that must be available. Defaults to 0.5.

    Returns:
        list[RecipeDTO]: List of recipes that can be made with the given ingredients

    Example:
        Request: GET /recipe/by-ingredients?ingredients=flour,eggs,milk&min_match_percentage=0.7

    Raises:
        HTTPException: 400 if min_match_percentage is not between 0 and 1
    """
    if not ingredients:
        raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")

    ingredient_list = [ing.strip() for ing in ingredients.split(",")]
    recipes = await service.get_by_ingredients(ingredient_list, min_match_percentage)
    
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found with these ingredients")
    
    return recipes


@router.get("/recipes/name/{recipe_name}", response_model=list[RecipeDTO])
@inject
async def get_recipe_by_name(
    recipe_name: str,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes by name.

    Args:
        recipe_name (str): Name of the recipe to find (partial match)
        service (IRecipeService): The injected service dependency.

    Returns:
        list[RecipeDTO]: List of recipes matching the name

    Raises:
        HTTPException: 404 if no recipes found
    """
    recipes = await service.get_by_name(recipe_name)
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")
    return recipes


@router.get("/recipes/preparation_time/{preparation_time}", response_model=list[RecipeDTO])
@inject
async def get_recipes_by_preparation_time(
    preparation_time: int,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes by preparation time.

    Args:
        preparation_time (int): Preparation time in minutes
        service (IRecipeService): The injected service dependency.

    Returns:
        list[dict]: List of recipes with given preparation time
    """
    recipes = await service.get_by_preparation_time(preparation_time)
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")
    return recipes


@router.get("/recipes/rating/{average_rating}", response_model=list[RecipeDTO])
@inject
async def get_recipes_by_rating(
    average_rating: float,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes by average rating.

    Args:
        average_rating (float): Minimum average rating
        service (IRecipeService): The injected service dependency.

    Returns:
        list[dict]: List of recipes with given or higher rating
    """
    recipes = await service.get_by_average_rating(average_rating)
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")
    return recipes


@router.get("/recipes/category/{category}", response_model=list[RecipeDTO])
@inject
async def get_recipes_by_category(
    category: str,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes by category.

    Args:
        category (str): Recipe category
        service (IRecipeService): The injected service dependency.

    Returns:
        list[dict]: List of recipes in given category
    """
    recipes = await service.get_by_category(category)
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")
    return recipes


@router.get("/recipes/author/{author_id}", response_model=list[RecipeDTO])
@inject
async def get_recipes_by_author(
    author_id: UUID,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes by author.

    Args:
        author_id (UUID): ID of the author
        service (IRecipeService): The injected service dependency.

    Returns:
        list[dict]: List of recipes by given author
    """
    recipes = await service.get_by_user(author_id)
    if not recipes:
        raise HTTPException(status_code=404, detail="No recipes found")
    return recipes


@router.get("/recipes/tag/{tag}", response_model=list[RecipeDTO])
@inject
async def get_recipe_by_tag(
    tag: str, 
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> list[RecipeDTO]:
    """Get recipes by tag.

    Args:
        tag (str): The tag to search for
        service (IRecipeService): The injected service dependency.

    Returns:
        list[RecipeDTO]: List of recipes with the specified tag
    """
    recipes = await service.get_by_tag(tag)
    if not recipes:
        raise HTTPException(status_code=404, detail=f"No recipes found with tag: {tag}")
    return recipes


@router.get("/recipes/{recipe_id}", response_model=RecipeDTO)
@inject
async def get_recipe_by_id(
    recipe_id: int,
    service: IRecipeService = Depends(Provide[Container.recipe_service])
) -> RecipeDTO:
    """Get recipe by ID.

    Args:
        recipe_id (int): ID of the recipe to find
        service (IRecipeService): The injected service dependency.

    Returns:
        dict: Recipe details if found

    Raises:
        HTTPException: 404 if recipe not found
    """
    recipe = await service.get_by_id(recipe_id)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.post("/recipes", response_model=RecipeDTO, status_code=201)
@inject
async def create_recipe(
    recipe: RecipeIn,
    service: IRecipeService = Depends(Provide[Container.recipe_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> RecipeDTO:
    """Create a new recipe.

    Required fields in request body:
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

    Example request body:
        {
            "name": "Chocolate Cake",
            "description": "Delicious chocolate cake recipe",
            "instructions": "Mix ingredients and bake...",
            "category": "Desserts",
            "ingredients": [
                "200g:flour",
                "100g:sugar",
                "50g:cocoa powder"
            ],
            "preparation_time": 60,
            "servings": 8,
            "difficulty": "medium",
            "steps": [
                "Preheat oven to 180°C",
                "Mix dry ingredients",
                "Add wet ingredients"
            ],
            "tags": ["dessert", "chocolate", "cake"]
        }

    Returns:
        RecipeDTO: Created recipe with generated ID and metadata

    Raises:
        HTTPException: 
            - 401: Unauthorized (missing or invalid token)
            - 400: Invalid input data
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        recipe_domain = Recipe(
            name=recipe.name,
            description=recipe.description,
            instructions=recipe.instructions,
            ingredients=recipe.ingredients,
            preparation_time=recipe.preparation_time,
            category=recipe.category,
            servings=recipe.servings,
            difficulty=recipe.difficulty,
            steps=recipe.steps,
            tags=recipe.tags,
            author=UUID(user_uuid)
        )

        created_recipe = await service.add_recipe(recipe_domain)
        if not created_recipe:
            raise HTTPException(
                status_code=400,
                detail="Failed to create recipe"
            )
        return created_recipe
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.put("/recipes/{recipe_id}", response_model=RecipeDTO)
@inject
async def update_recipe(
    recipe_id: int,
    updated_recipe: RecipeIn,
    service: IRecipeService = Depends(Provide[Container.recipe_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> RecipeDTO:
    """An endpoint for updating recipe data.

    Args:
        recipe_id (int): The id of the recipe.
        updated_recipe (RecipeIn): The updated recipe details.
        service (IRecipeService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Returns:
        dict: The updated recipe details.
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        recipe = await service.get_by_id(recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        if recipe.author != UUID(user_uuid) and not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Not authorized to update this recipe")

        recipe_domain = Recipe(
            name=updated_recipe.name,
            description=updated_recipe.description,
            instructions=updated_recipe.instructions,
            ingredients=updated_recipe.ingredients,
            preparation_time=updated_recipe.preparation_time,
            category=updated_recipe.category,
            servings=updated_recipe.servings,
            difficulty=updated_recipe.difficulty,
            author=UUID(user_uuid)
        )

        updated = await service.update_recipe(recipe_id, recipe_domain)
        if updated is None:
            raise HTTPException(status_code=400, detail="Failed to update recipe")
        return updated

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.delete("/recipes/{recipe_id}")
@inject
async def delete_recipe(
    recipe_id: int,
    service: IRecipeService = Depends(Provide[Container.recipe_service]),
    user_service: IUserService = Depends(Provide[Container.user_service]),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """An endpoint for deleting recipes.

    Args:
        recipe_id (int): The id of the recipe.
        service (IRecipeService): The injected service dependency.
        user_service (IUserService): The injected user service dependency.
        credentials (HTTPAuthorizationCredentials): The credentials.

    Raises:
        HTTPException: 404 if recipe does not exist or 403 if unauthorized.
    """
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_uuid = payload.get("sub")
        if not user_uuid:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        recipe = await service.get_by_id(recipe_id)
        if recipe is None:
            raise HTTPException(status_code=404, detail="Recipe not found")

        if recipe.author != UUID(user_uuid) and not await is_admin(user_uuid, user_service):
            raise HTTPException(status_code=403, detail="Not authorized to delete this recipe")

        if await service.delete_recipe(recipe_id):
            return {"message": "Recipe deleted successfully"}
        raise HTTPException(status_code=400, detail="Failed to delete recipe")

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
