from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import UUID

from sqlalchemy import select, func

from mealapi.core.domain.recipe import Recipe
from mealapi.db import database
from mealapi.db import recipe_table, rating_table, comment_table
from mealapi.infrastructure.services.ai_detector import AIDetector
import unicodedata


class RecipeRepository:
    """A class representing recipe DB repository."""

    async def get_all_recipes(self) -> List[Dict[str, Any]]:
        """The getting all recipes from the data storage.

        Returns:
            List[Dict[str, Any]]: All recipes in the data storage.
        """
        return await self._fetch_recipes_with_related(True)

    async def get_by_id(self, recipe_id: int) -> Dict[str, Any] | None:
        """Get a recipe from the data storage by id.

        Args:
            recipe_id (int): The id of the recipe.

        Returns:
            Dict[str, Any] | None: The recipe data if exists.
        """
        # Get recipe with ratings
        query = (
            select(
                recipe_table,
                rating_table,
                func.avg(rating_table.c.value).over(partition_by=recipe_table.c.id).label('average_rating')
            )
            .join_from(recipe_table, rating_table, recipe_table.c.id == rating_table.c.recipe_id, isouter=True)
            .where(recipe_table.c.id == recipe_id)
        )
        recipe = await database.fetch_one(query)
        if not recipe:
            return None

        # Get comments for this recipe
        comments_query = (
            select(
                comment_table,
                rating_table.c.value.label('rating_value')
            )
            .join_from(comment_table, rating_table, comment_table.c.rating_id == rating_table.c.id, isouter=True)
            .where(comment_table.c.recipe_id == recipe_id)
        )
        comments = await database.fetch_all(comments_query)

        # Get ratings for this recipe
        ratings_query = (
            select(rating_table)
            .where(rating_table.c.recipe_id == recipe_id)
        )
        ratings = await database.fetch_all(ratings_query)

        # Prepare recipe data
        recipe_dict = dict(recipe)
        recipe_dict['ratings'] = [dict(rating) for rating in ratings]
        
        # Properly handle comments with and without ratings
        comments_list = []
        for comment in comments:
            comment_dict = {
                'id': comment['id'],
                'author': comment['author'],
                'recipe_id': comment['recipe_id'],
                'created_at': comment['created_at'],
                'content': comment['content'],
                'rating_id': comment['rating_id'],
                'rating_value': comment['rating_value']
            }
            comments_list.append(comment_dict)
            
        recipe_dict['comments'] = comments_list
        recipe_dict['average_rating'] = round(recipe['average_rating'], 2) if\
            recipe['average_rating'] is not None else None

        return recipe_dict

    async def get_by_name(self, recipe_name: str) -> List[Dict[str, Any]]:
        """Get recipes from the data storage by partial name match.

        Args:
            recipe_name (str): Part of the recipe name to search for.

        Returns:
            List[Dict[str, Any]]: All recipes that contain the given name.
        """
        return await self._fetch_recipes_with_related(recipe_table.c.name.ilike(f"%{recipe_name}%"))

    async def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get recipes by category.

        Args:
            category (str): The category to filter by

        Returns:
            List[Dict[str, Any]]: All recipes in the specified category
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

            result.append(recipe_dict)

        return result

    async def get_by_tag(self, tag: str) -> List[Dict[str, Any]]:
        """Get recipes by tag.

        Args:
            tag (str): The tag to filter by

        Returns:
            List[Dict[str, Any]]: All recipes with the specified tag
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

                result.append(recipe_dict)

            return result

        except Exception as e:
            raise Exception(f"Error fetching recipes by tag {tag}: {str(e)}")

    async def get_by_average_rating(self, average_rating: float) -> List[Dict[str, Any]]:
        """Get recipes by minimum average rating.

        Args:
            average_rating (float): Minimum average rating to filter by

        Returns:
            List[Dict[str, Any]]: Recipes with average rating >= specified value

        Raises:
            InvalidParameterError: If rating is not between 0 and 5
        """

        try:
            # Fetch all recipes with ratings and comments
            recipes = await self._fetch_recipes_with_related(True)
            
            # Filter recipes by average rating
            filtered_recipes = [
                recipe for recipe in recipes 
                if recipe['average_rating'] is not None 
                and recipe['average_rating'] >= average_rating
            ]
            
            return filtered_recipes

        except Exception as e:
            raise Exception(f"Error fetching recipes with average rating >= {average_rating}: {str(e)}")

    async def get_by_preparation_time(self, preparation_time: int) -> List[Dict[str, Any]]:
        """Get recipes by preparation time.

        Args:
            preparation_time (int): The preparation time to filter by

        Returns:
            List[Dict[str, Any]]: Recipes with specified preparation time

        Raises:
            InvalidParameterError: If preparation time is not positive
        """
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

            result.append(recipe_dict)

        return result

    async def get_by_ingredients(self, ingredients: List[str], min_match_percentage: float) -> List[Dict[str, Any]]:
        """Get recipes that can be made with the given ingredients.

        Args:
            ingredients (List[str]): List of ingredients the user has
            min_match_percentage (float): Minimum percentage of recipe ingredients that must be available (0.0 to 1.0)

        Returns:
            List[Dict[str, Any]]: Recipes that can be made with the given ingredients, sorted by match percentage

        Raises:
            Exception: If min_match_percentage is not between 0 and 1
        """
        if not ingredients:
            raise Exception("Ingredients list cannot be empty")

        if not 0 <= min_match_percentage <= 1:
            raise Exception("min_match_percentage must be between 0 and 1")

        # Fetch all recipes with ratings and comments
        recipes = await self._fetch_recipes_with_related(True)

        # Normalize search ingredients using the same logic as in Pydantic model
        normalized_search_ingredients = [
            ''.join(
                char for char in unicodedata.normalize('NFKD', ing.strip().lower())
                if unicodedata.category(char) != 'Mn'
            )
            for ing in ingredients
        ]

        matching_recipes = []
        for recipe in recipes:
            recipe_ingredients = []
            for ing_str in recipe['ingredients']:
                ingredient = ing_str.split(':', 1)[1] if ':' in ing_str else ing_str
                normalized_ing = ''.join(
                    char for char in unicodedata.normalize('NFKD', ingredient.strip().lower())
                    if unicodedata.category(char) != 'Mn'
                )
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
                recipe['match_percentage'] = match_percentage
                matching_recipes.append(recipe)

        # Sort by match percentage (highest first)
        matching_recipes.sort(key=lambda x: x['match_percentage'], reverse=True)
        return matching_recipes

    async def get_by_user(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get all recipes created by a specific user.

        Args:
            user_id (UUID): The ID of the user whose recipes we want to retrieve

        Returns:
            List[Dict[str, Any]]: All recipes created by the specified user
        """
        try:
            recipes = await self._fetch_recipes_with_related(recipe_table.c.author == user_id)
            return recipes
        except Exception as e:
            raise Exception(f"Error fetching recipes for user {user_id}: {str(e)}")

    async def add_recipe(self, recipe: Recipe, author_id: UUID) -> Dict[str, Any] | None:
        """The adding recipe to the data storage.

        Args:
            recipe (Recipe): The recipe.
            author_id (UUID): The author id.

        Returns:
            Dict[str, Any] | None: The newly created recipe.
        """
        ai_score = await AIDetector.detect_ai_text(recipe.instructions)
        # Prepare the data for writing
        recipe_data = {
            "name": recipe.name,
            "description": recipe.description,
            "instructions": recipe.instructions,
            "category": recipe.category,
            "author": author_id,
            "created_at": datetime.now(timezone.utc),
            "preparation_time": recipe.preparation_time,
            "servings": recipe.servings,
            "difficulty": recipe.difficulty,
            "average_rating": None,
            "ai_detected": ai_score if ai_score is not None else None,
            "ingredients": recipe.ingredients,
            "steps": recipe.steps,
            "tags": recipe.tags
        }

        # Add a recipe
        query = recipe_table.insert().values(**recipe_data)
        recipe_id = await database.execute(query)

        # Download the added recipe
        return await self.get_by_id(recipe_id)

    async def create_recipe(self, recipe: Recipe) -> Dict[str, Any] | None:
        """Create a new recipe.

        Args:
            recipe (Recipe): The recipe to create.

        Returns:
            Dict[str, Any] | None: The newly created recipe.
        """
        ai_score = await AIDetector.detect_ai_text(recipe.instructions)
        
        # Get recipe data from Pydantic model, excluding certain fields
        recipe_data = recipe.model_dump(exclude={'id', 'created_at', 'average_rating'})
        recipe_data['ai_detected'] = ai_score

        # Add recipe
        query = recipe_table.insert().values(**recipe_data)
        recipe_id = await database.execute(query)

        # Get added recipe
        return await self.get_by_id(recipe_id)

    async def update_recipe(self, recipe_id: int, recipe: Recipe) -> Dict[str, Any] | None:
        """Update an existing recipe.

        Args:
            recipe_id (int): The ID of the recipe to update.
            recipe (Recipe): The updated recipe data.

        Returns:
            Dict[str, Any] | None: The updated recipe.
        """
        old_recipe = await self.get_by_id(recipe_id)
        if not old_recipe:
            return None

        ai_score = await AIDetector.detect_ai_text(recipe.instructions)
        
        # Get recipe data from Pydantic model, excluding certain fields
        recipe_data = recipe.model_dump(exclude={'id', 'created_at', 'average_rating'})
        recipe_data['ai_detected'] = ai_score

        # Update recipe
        query = recipe_table.update().where(recipe_table.c.id == recipe_id).values(**recipe_data)
        await database.execute(query)

        # Get updated recipe
        return await self.get_by_id(recipe_id)

    async def delete_recipe(self, recipe_id: int) -> bool:
        """Delete a recipe from the data storage.

        Args:
            recipe_id (int): The id of the recipe.

        Returns:
            bool: True if recipe was deleted, False if it didn't exist.
        """
        try:
            recipe = await self.get_by_id(recipe_id)
            if recipe:
                query = recipe_table.delete().where(recipe_table.c.id == recipe_id)
                await database.execute(query)
                return True
            return False
        except Exception as e:
            raise Exception(f"Error deleting recipe {recipe_id}: {str(e)}")

    async def _get_by_id(self, recipe_id: int) -> Dict[str, Any] | None:
        """A private method getting recipe from the DB based on its ID.

        Args:
            recipe_id (int): The ID of the recipe.

        Returns:
            Dict[str, Any] | None: Recipe record if exists.
        """
        try:
            query = (
                select(recipe_table, rating_table)
                .join_from(recipe_table, rating_table, recipe_table.c.id == rating_table.c.recipe_id, isouter=True)
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

    async def _fetch_recipes_with_related(self, where_clause) -> List[Dict[str, Any]]:
        """Fetch recipes with their ratings and comments.

        Args:
            where_clause: SQLAlchemy where clause for filtering recipes

        Returns:
            List[Dict[str, Any]]: List of recipe dictionaries with related data
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
            .join_from(recipe_table, rating_table, recipe_table.c.id == rating_table.c.recipe_id, isouter=True)
            .join_from(recipe_table, comment_table, recipe_table.c.id == comment_table.c.recipe_id, isouter=True)
        )

        if where_clause is not True: 
            query = query.where(where_clause)

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
                    'ai_detected': row['ai_detected'],
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