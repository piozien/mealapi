"""Module providing containers injecting dependencies."""

from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory, Singleton

from mealapi.infrastructure.repositories.user import UserRepository
from mealapi.infrastructure.repositories.recipedb import RecipeRepository
from mealapi.infrastructure.repositories.commentdb import CommentRepository
from mealapi.infrastructure.repositories.reportdb import ReportRepository

from mealapi.infrastructure.services.recipe import RecipeService
from mealapi.infrastructure.services.comment import CommentService
from mealapi.infrastructure.services.user import UserService
from mealapi.infrastructure.services.report import ReportService

class Container(DeclarativeContainer):
    """Container class for dependency injecting purposes."""
    recipe_repository = Singleton(RecipeRepository)
    comment_repository = Singleton(CommentRepository)
    report_repository = Singleton(ReportRepository)
    user_repository = Singleton(UserRepository)

    recipe_service = Factory(
        RecipeService,
        recipe_repository=recipe_repository,
    )
    comment_service = Factory(
        CommentService,
        comment_repository=comment_repository,
    )
    report_service = Factory(
        ReportService,
        repository=report_repository,
    )
    user_service = Factory(
        UserService,
        repository=user_repository,
    )
