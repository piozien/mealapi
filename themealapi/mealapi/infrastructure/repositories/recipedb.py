from datetime import datetime, timezone
from typing import Any, Iterable, List, Dict
from uuid import UUID

from databases.interfaces import Record
from sqlalchemy import select, any_, func
from sqlalchemy.exc import InvalidRequestError

from mealapi.core.domain.recipe import Recipe
from mealapi.infrastructure.dto.recipedto import RecipeDTO
from mealapi.core.repositories.irecipe import IRecipeRepository
from mealapi.infrastructure.utils.recipe_mapper import RecipeMapper
from mealapi.db import database
from mealapi.db import recipe_table, rating_table, comment_table
import aiohttp


class RecipeRepository(IRecipeRepository):
    """A class representing recipe DB repository."""

    async def get_all_recipes(self) -> Iterable[Any]:
        """The getting all recipes from the data storage.

        Returns:
            Iterable[Any]: All recipes in the data storage.
        """
        query = select(recipe_table).select_from(recipe_table)
        recipes = await database.fetch_all(query)

        if not recipes:
            return []

        recipe_ids = [recipe['id'] for recipe in recipes]
        ratings_query = (
            select(rating_table)
            .where(rating_table.c.recipe_id.in_(recipe_ids))
        )
        ratings = await database.fetch_all(ratings_query)

        comments_query = (
            select(comment_table)
            .where(comment_table.c.recipe_id.in_(recipe_ids))
        )
        comments = await database.fetch_all(comments_query)

        ratings_by_recipe = {}
        comments_by_recipe = {}

        for rating in ratings:
            recipe_id = rating['recipe_id']
            if recipe_id not in ratings_by_recipe:
                ratings_by_recipe[recipe_id] = []
            ratings_by_recipe[recipe_id].append(dict(rating))

        for comment in comments:
            recipe_id = comment['recipe_id']
            if recipe_id not in comments_by_recipe:
                comments_by_recipe[recipe_id] = []
            comment_dict = dict(comment)
            if comment_dict.get('rating_id') is None:
                comment_dict.pop('rating_id', None)
            comments_by_recipe[recipe_id].append(comment_dict)

        result = []
        for recipe in recipes:
            recipe_dict = dict(recipe)
            recipe_dict['ratings'] = ratings_by_recipe.get(recipe_dict['id'], [])
            recipe_dict['comments'] = comments_by_recipe.get(recipe_dict['id'], [])

            ratings_values = [r['value'] for r in recipe_dict['ratings']]
            recipe_dict['average_rating'] = round(sum(ratings_values) / len(ratings_values), 2) if ratings_values else None
            
            result.append(RecipeDTO.from_record(recipe_dict))

        return result

    async def get_by_id(self, recipe_id: int) -> Any | None:
        """Get a recipe from the data storage by id.

        Args:
            recipe_id (int): The id of the recipe.

        Returns:
            Any | None: The recipe data if exists.
        """
        # Get recipe with ratings
        query = (
            select(recipe_table, rating_table)
            .select_from(recipe_table)
            .outerjoin(rating_table, recipe_table.c.id == rating_table.c.recipe_id)
            .where(recipe_table.c.id == recipe_id)
        )
        recipe = await database.fetch_one(query)
        if not recipe:
            return None

        # Get comments for this recipe
        comments_query = (
            select(comment_table)
            .select_from(comment_table)
            .where(comment_table.c.recipe_id == recipe_id)
        )
        comments = await database.fetch_all(comments_query)

        # Get ratings for this recipe
        ratings_query = (
            select(rating_table)
            .select_from(rating_table)
            .where(rating_table.c.recipe_id == recipe_id)
        )
        ratings = await database.fetch_all(ratings_query)

        # Prepare recipe data
        recipe_dict = dict(recipe)
        recipe_dict['ratings'] = [
            {
                'id': rating['id'],
                'value': rating['value'],
                'recipe_id': rating['recipe_id'],
                'author': rating['author'],
                'created_at': rating['created_at']
            }
            for rating in ratings
        ]
        recipe_dict['comments'] = [dict(comment) for comment in comments]
        
        return RecipeDTO.from_record(recipe_dict)

    async def get_by_name(self, recipe_name: str) -> Iterable[Any]:
        """Get recipes from the data storage by partial name match.

        Args:
            recipe_name (str): Part of the recipe name to search for.

        Returns:
            Iterable[Any]: All recipes that contain the given name.
        """
        try:
            return await self._fetch_recipes_with_related(recipe_table.c.name.ilike(f"%{recipe_name}%"))
        except Exception as e:
            raise Exception(f"Error fetching recipes with name {recipe_name}: {str(e)}")

    async def get_by_category(self, category: str) -> Iterable[Any]:
        """Get recipes by category.

        Args:
            category (str): The category to filter by

        Returns:
            Iterable[Any]: All recipes in the specified category
        """
        query = (
            select(recipe_table)
            .where(recipe_table.c.category.ilike(f"%{category.lower()}%"))
        )
        recipes = await database.fetch_all(query)

        # Get all ratings for these recipes
        recipe_ids = [recipe['id'] for recipe in recipes]
        if recipe_ids:
            ratings_query = (
                select(rating_table)
                .where(rating_table.c.recipe_id.in_(recipe_ids))
            )
            all_ratings = await database.fetch_all(ratings_query)

            # Get all comments for these recipes
            comments_query = (
                select(comment_table)
                .where(comment_table.c.recipe_id.in_(recipe_ids))
            )
            all_comments = await database.fetch_all(comments_query)

            # Group ratings and comments by recipe
            ratings_by_recipe = {}
            comments_by_recipe = {}

            for rating in all_ratings:
                recipe_id = rating['recipe_id']
                if recipe_id not in ratings_by_recipe:
                    ratings_by_recipe[recipe_id] = []
                ratings_by_recipe[recipe_id].append(dict(rating))

            for comment in all_comments:
                recipe_id = comment['recipe_id']
                if recipe_id not in comments_by_recipe:
                    comments_by_recipe[recipe_id] = []
                comments_by_recipe[recipe_id].append(dict(comment))
        else:
            ratings_by_recipe = {}
            comments_by_recipe = {}

        result = []
        for recipe in recipes:
            recipe_dict = dict(recipe)
            recipe_dict['ratings'] = ratings_by_recipe.get(recipe_dict['id'], [])
            recipe_dict['comments'] = comments_by_recipe.get(recipe_dict['id'], [])

            # Calculate average rating
            ratings = recipe_dict['ratings']
            if ratings:
                recipe_dict['average_rating'] = round(sum(r['value'] for r in ratings) / len(ratings), 2)
            else:
                recipe_dict['average_rating'] = None

            result.append(RecipeDTO.from_record(recipe_dict))

        return result

    async def get_by_tag(self, tag: str) -> Iterable[Any]:
        """Get recipes by tag.

        Args:
            tag (str): The tag to filter by

        Returns:
            Iterable[Any]: All recipes with the specified tag
        """
        try:
            # Get recipes with the specified tag
            query = (
                select(recipe_table)
                .where(func.array_position(recipe_table.c.tags, tag.lower()) != None)
            )
            
            recipes = await database.fetch_all(query)

            # Get ratings and comments for these recipes
            recipe_ids = [recipe['id'] for recipe in recipes]
            
            if recipe_ids:
                # Get ratings for these recipes
                ratings_query = select(rating_table).where(rating_table.c.recipe_id.in_(recipe_ids))
                ratings = await database.fetch_all(ratings_query)
                
                # Get comments for these recipes
                comments_query = select(comment_table).where(comment_table.c.recipe_id.in_(recipe_ids))
                comments = await database.fetch_all(comments_query)
                
                # Group ratings and comments by recipe_id
                ratings_by_recipe = {}
                comments_by_recipe = {}
                
                for rating in ratings:
                    recipe_id = rating['recipe_id']
                    if recipe_id not in ratings_by_recipe:
                        ratings_by_recipe[recipe_id] = []
                    ratings_by_recipe[recipe_id].append(dict(rating))
                    
                for comment in comments:
                    recipe_id = comment['recipe_id']
                    if recipe_id not in comments_by_recipe:
                        comments_by_recipe[recipe_id] = []
                    comments_by_recipe[recipe_id].append(dict(comment))
            else:
                ratings_by_recipe = {}
                comments_by_recipe = {}

            # Combine all data and create DTOs
            result = []
            for recipe in recipes:
                recipe_dict = dict(recipe)
                recipe_dict['ratings'] = ratings_by_recipe.get(recipe_dict['id'], [])
                recipe_dict['comments'] = comments_by_recipe.get(recipe_dict['id'], [])
                
                # Calculate average rating
                ratings = recipe_dict['ratings']
                if ratings:
                    recipe_dict['average_rating'] = sum(r['value'] for r in ratings) / len(ratings)
                else:
                    recipe_dict['average_rating'] = 0.0
                
                result.append(RecipeDTO.from_record(recipe_dict))
            
            return result

        except Exception as e:
            raise Exception(f"Error fetching recipes by tag {tag}: {str(e)}")

    async def get_by_average_rating(self, average_rating: float) -> Iterable[Any]:
        """Get recipes by minimum average rating.

        Args:
            average_rating (float): Minimum average rating to filter by

        Returns:
            Iterable[Any]: Recipes with average rating >= specified value

        Raises:
            InvalidParameterError: If rating is not between 0 and 5
        """
        if not 0 <= average_rating <= 5:
            raise InvalidParameterError("Rating must be between 0 and 5")

        subquery = (
            select([recipe_table.c.id.label('recipe_id')])
            .select_from(recipe_table)
            .join(rating_table, recipe_table.c.id == rating_table.c.recipe_id)
            .group_by(recipe_table.c.id)
            .having(func.avg(rating_table.c.value) >= average_rating)
            .alias('avg_ratings')
        )

        try:
            return await self._fetch_recipes_with_related(recipe_table.c.id.in_(select([subquery.c.recipe_id])))
        except Exception as e:
            raise Exception(f"Error fetching recipes with average rating >= {average_rating}: {str(e)}")

    async def get_by_preparation_time(self, preparation_time: int) -> Iterable[Any]:
        """Get recipes by preparation time.

        Args:
            preparation_time (int): The preparation time to filter by

        Returns:
            Iterable[Any]: Recipes with specified preparation time

        Raises:
            InvalidParameterError: If preparation time is not positive
        """
        if preparation_time <= 0:
            raise InvalidParameterError("Preparation time must be positive")

        query = (
            select(recipe_table)
            .select_from(recipe_table)
            .where(recipe_table.c.preparation_time == preparation_time)
        )
        recipes = await database.fetch_all(query)

        # Get all ratings for these recipes
        recipe_ids = [recipe['id'] for recipe in recipes]
        if recipe_ids:
            ratings_query = (
                select(rating_table)
                .where(rating_table.c.recipe_id.in_(recipe_ids))
            )
            all_ratings = await database.fetch_all(ratings_query)

            # Get all comments for these recipes
            comments_query = (
                select(comment_table)
                .where(comment_table.c.recipe_id.in_(recipe_ids))
            )
            all_comments = await database.fetch_all(comments_query)

            # Group ratings and comments by recipe
            ratings_by_recipe = {}
            comments_by_recipe = {}

            for rating in all_ratings:
                recipe_id = rating['recipe_id']
                if recipe_id not in ratings_by_recipe:
                    ratings_by_recipe[recipe_id] = []
                ratings_by_recipe[recipe_id].append(dict(rating))

            for comment in all_comments:
                recipe_id = comment['recipe_id']
                if recipe_id not in comments_by_recipe:
                    comments_by_recipe[recipe_id] = []
                comments_by_recipe[recipe_id].append(dict(comment))
        else:
            ratings_by_recipe = {}
            comments_by_recipe = {}

        result = []
        for recipe in recipes:
            recipe_dict = dict(recipe)
            recipe_dict['ratings'] = ratings_by_recipe.get(recipe_dict['id'], [])
            recipe_dict['comments'] = comments_by_recipe.get(recipe_dict['id'], [])

            # Calculate average rating
            ratings = recipe_dict['ratings']
            if ratings:
                recipe_dict['average_rating'] = round(sum(r['value'] for r in ratings) / len(ratings), 2)
            else:
                recipe_dict['average_rating'] = None

            result.append(RecipeDTO.from_record(recipe_dict))

        return result

    async def get_by_ingredients(self, ingredients: List[str], min_match_percentage: float) -> Iterable[Any]:
        """Get recipes that can be made with the given ingredients.

        Args:
            ingredients (List[str]): List of ingredients the user has
            min_match_percentage (float): Minimum percentage of recipe ingredients that must be available (0.0 to 1.0)

        Returns:
            Iterable[Any]: Recipes that can be made with the given ingredients, sorted by match percentage

        Raises:
            Exception: If min_match_percentage is not between 0 and 1
        """
        from mealapi.infrastructure.utils.recipe_mapper import RecipeMapper

        if not ingredients:
            raise Exception("Ingredients list cannot be empty")

        if not 0 <= min_match_percentage <= 1:
            raise Exception("min_match_percentage must be between 0 and 1")

        query = select(recipe_table).select_from(recipe_table)
        recipes = await database.fetch_all(query)

        normalized_search_ingredients = [
            RecipeMapper.normalize_string(ing.strip().lower())
            for ing in ingredients
        ]

        matching_recipes = []
        for recipe in recipes:
            recipe_ingredients = []
            for ing_str in recipe.ingredients:
                ingredient = ing_str.split(':', 1)[1] if ':' in ing_str else ing_str
                normalized_ing = RecipeMapper.normalize_string(ingredient.strip().lower())
                if normalized_ing:
                    recipe_ingredients.append(normalized_ing)

            if not recipe_ingredients:
                continue

            matching_ingredients = sum(
                1 for ing in recipe_ingredients
                if any(search_ing in ing for search_ing in normalized_search_ingredients)
            )

            match_percentage = matching_ingredients / len(recipe_ingredients)
            if match_percentage >= min_match_percentage:
                recipe_dict = {
                    'id': recipe['id'],
                    'name': recipe['name'],
                    'description': recipe['description'],
                    'instructions': recipe['instructions'],
                    'category': recipe['category'],
                    'ingredients': recipe['ingredients'],
                    'preparation_time': recipe['preparation_time'],
                    'servings': recipe['servings'],
                    'difficulty': recipe['difficulty'],
                    'author': recipe['author'],
                    'created_at': recipe['created_at'],
                    'steps': recipe['steps'],
                    'tags': recipe['tags'],
                    'match_percentage': match_percentage
                }
                matching_recipes.append(recipe_dict)

        matching_recipes.sort(key=lambda x: x['match_percentage'], reverse=True)
        return [RecipeDTO.from_record(recipe) for recipe in matching_recipes]

    async def get_by_user(self, user_id: UUID) -> Iterable[Any]:
        """Get all recipes created by a specific user.

        Args:
            user_id (UUID): The ID of the user whose recipes we want to retrieve

        Returns:
            Iterable[Any]: All recipes created by the specified user
        """
        try:
            recipes = await self._fetch_recipes_with_related(recipe_table.c.author == user_id)
            return [RecipeDTO.from_record(recipe) for recipe in recipes]
        except Exception as e:
            raise Exception(f"Error fetching recipes for user {user_id}: {str(e)}")

    async def _detect_ai_text(self, text: str) -> float:
        """Detect if text was generated by AI using Sapling API.

        Args:
            text (str): Text to analyze

        Returns:
            float: AI detection score between 0 and 1
        """
        url = "https://api.sapling.ai/api/v1/aidetect"
        payload = {
            "key": "PRTR0IVRONYESGVENTVZODNEITI2SB0V",
            "text": text
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    response_data = await response.json()
                    score = response_data.get('score', 0.0)
                    return round(score, 2)
        except Exception as e:
            print(f"Error detecting AI text: {str(e)}")
            return 0.0

    async def add_recipe(self, recipe: Recipe, author: UUID) -> Any | None:
        """The adding a new recipe to the data storage.

        Args:
            recipe (Recipe): The attributes of the recipe.
            author (UUID): The author of the recipe.

        Returns:
            Any | None: The newly created recipe.
        """
        try:
            RecipeMapper.validate(recipe)

            # Detect AI generated text
            ai_score = await self._detect_ai_text(recipe.instructions)

            recipe_data = {
                "name": recipe.name.lower(),
                "description": recipe.description,
                "instructions": recipe.instructions,
                "category": recipe.category.lower(),
                "ingredients": RecipeMapper.ingredients_to_strings(recipe.ingredients),
                "preparation_time": recipe.preparation_time,
                "servings": recipe.servings,
                "difficulty": recipe.difficulty,
                "author": author,
                "created_at": datetime.now(timezone.utc),
                "steps": recipe.steps or [],
                "tags": recipe.tags or [],
                "average_rating": 0.0,
                "ai_detected": ai_score
            }

            query = recipe_table.insert().values(**recipe_data).returning(recipe_table.c.id)
            new_recipe_id = await database.execute(query)

            new_recipe = await self._get_by_id(new_recipe_id)
            if new_recipe:
                recipe_dict = dict(new_recipe)
                recipe_dict['comments'] = []
                recipe_dict['ratings'] = []
                recipe_dict['ai_detected'] = ai_score
                return RecipeDTO.from_record(recipe_dict)
            return None

        except Exception as e:
            raise

    async def update_recipe(self, recipe_id: int, recipe: Recipe) -> Any | None:
        """The updating recipe data in the data storage.

        Args:
            recipe_id (int): The id of the recipe.
            recipe (Recipe): The attributes of the recipe.

        Returns:
            Any | None: The updated recipe.
        """
        try:
            RecipeMapper.validate(recipe)

            recipe_data = {
                "name": recipe.name.lower(),
                "description": recipe.description,
                "instructions": recipe.instructions,
                "category": recipe.category.lower(),
                "ingredients": RecipeMapper.ingredients_to_strings(recipe.ingredients),
                "preparation_time": recipe.preparation_time,
                "servings": recipe.servings,
                "difficulty": recipe.difficulty,
                "steps": recipe.steps or [],
                "tags": recipe.tags or []
            }

            query = (
                recipe_table.update()
                .where(recipe_table.c.id == recipe_id)
                .values(**recipe_data)
            )
            await database.execute(query)

            # Get updated recipe with ratings and comments
            recipe = await self._get_by_id(recipe_id)
            if recipe:
                recipe_dict = dict(recipe)
                
                # Get ratings
                ratings_query = select(rating_table).where(rating_table.c.recipe_id == recipe_id)
                ratings = await database.fetch_all(ratings_query)
                recipe_dict['ratings'] = [dict(r) for r in ratings] if ratings else []
                
                # Get comments
                comments_query = select(comment_table).where(comment_table.c.recipe_id == recipe_id)
                comments = await database.fetch_all(comments_query)
                recipe_dict['comments'] = [dict(c) for c in comments] if comments else []
                
                # Calculate average rating
                if recipe_dict['ratings']:
                    recipe_dict['average_rating'] = sum(r['value'] for r in recipe_dict['ratings']) / len(recipe_dict['ratings'])
                else:
                    recipe_dict['average_rating'] = 0.0
                
                return RecipeDTO.from_record(recipe_dict)
            return None

        except Exception as e:
            raise Exception(f"Error updating recipe {recipe_id}: {str(e)}")

    async def delete_recipe(self, recipe_id: int) -> bool:
        """The updating removing recipe from the data storage.

        Args:
            recipe_id (int): The id of the recipe.
        """
        try:
            recipe = await self._get_by_id(recipe_id)
            if recipe:
                query = recipe_table.delete().where(recipe_table.c.id == recipe_id)
                await database.execute(query)
                return True
            return False
        except Exception as e:
            raise Exception(f"Error deleting recipe {recipe_id}: {str(e)}")

    async def _get_by_id(self, recipe_id: int) -> Record | None:
        """A private method getting recipe from the DB based on its ID.

        Args:
            recipe_id (int): The ID of the recipe.

        Returns:
            Any | None: Recipe record if exists.
        """
        try:
            query = (
                select(recipe_table, rating_table)
                .select_from(recipe_table)
                .outerjoin(rating_table, recipe_table.c.id == rating_table.c.recipe_id)
                .where(recipe_table.c.id == recipe_id)
            )
            return await database.fetch_one(query)
        except Exception as e:
            raise Exception(f"Error getting recipe {recipe_id}: {str(e)}")

    async def _calculate_average_rating(self, recipe_id: int) -> float | None:
        """Calculate average rating for a recipe based on ratings.

        Args:
            recipe_id (int): The id of the recipe

        Returns:
            float | None: The average rating, or None if no ratings
        """
        query = (
            select([func.avg(rating_table.c.value)])
            .where(rating_table.c.recipe_id == recipe_id)
        )
        result = await database.fetch_val(query)
        return round(result, 2) if result is not None else None

    async def _fetch_recipes_with_related(self, where_clause) -> List[Dict]:
        """Fetch recipes with their ratings and comments.

        Args:
            where_clause: SQLAlchemy where clause for filtering recipes

        Returns:
            List[Dict]: List of recipe dictionaries with related data
        """
        query = (
            select(
                recipe_table,
                rating_table.c.id.label('rating_id'),
                rating_table.c.value.label('rating_value'),
                rating_table.c.author.label('rating_author'),
                rating_table.c.created_at.label('rating_created_at'),
                comment_table.c.id.label('comment_id'),
                comment_table.c.content.label('comment_content'),
                comment_table.c.author.label('comment_author'),
                comment_table.c.created_at.label('comment_created_at'),
                comment_table.c.rating_id.label('comment_rating_id'),
                func.avg(rating_table.c.value).over(partition_by=recipe_table.c.id).label('average_rating')
            )
            .select_from(recipe_table)
            .outerjoin(rating_table, recipe_table.c.id == rating_table.c.recipe_id)
            .outerjoin(comment_table, recipe_table.c.id == comment_table.c.recipe_id)
            .where(where_clause)
        )
        
        rows = await database.fetch_all(query)
        if not rows:
            return []

        # Group results by recipe
        recipes_map = {}
        for row in rows:
            recipe_id = row['id']
            if recipe_id not in recipes_map:
                recipe_dict = {
                    'id': row['id'],
                    'name': row['name'],
                    'description': row['description'],
                    'instructions': row['instructions'],
                    'category': row['category'],
                    'ingredients': row['ingredients'],
                    'preparation_time': row['preparation_time'],
                    'servings': row['servings'],
                    'difficulty': row['difficulty'],
                    'author': row['author'],
                    'created_at': row['created_at'],
                    'steps': row['steps'],
                    'tags': row['tags'],
                    'ratings': [],
                    'comments': [],
                    'average_rating': round(row['average_rating'], 2) if row['average_rating'] is not None else None
                }
                recipes_map[recipe_id] = recipe_dict

            # Add rating if exists and not duplicate
            if row['rating_id'] and not any(r['id'] == row['rating_id'] for r in recipes_map[recipe_id]['ratings']):
                rating = {
                    'id': row['rating_id'],
                    'value': row['rating_value'],
                    'recipe_id': recipe_id,
                    'author': row['rating_author'],
                    'created_at': row['rating_created_at']
                }
                recipes_map[recipe_id]['ratings'].append(rating)

            # Add comment if exists and not duplicate
            if row['comment_id'] and not any(c['id'] == row['comment_id'] for c in recipes_map[recipe_id]['comments']):
                comment = {
                    'id': row['comment_id'],
                    'content': row['comment_content'],
                    'recipe_id': recipe_id,
                    'author': row['comment_author'],
                    'created_at': row['comment_created_at'],
                    'rating_id': row['comment_rating_id']
                }
                recipes_map[recipe_id]['comments'].append(comment)

        return list(recipes_map.values())
