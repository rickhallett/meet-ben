from pathlib import Path
import frontmatter
from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateError, meta

"""
Prompt Management Module

This module provides functionality for loading and rendering prompt templates with frontmatter.
It uses Jinja2 for template rendering and python-frontmatter for metadata handling,
implementing a singleton pattern for template environment management.
"""


class PromptManager:
    """Manager class for handling prompt templates and their metadata.

    This class provides functionality to load prompt templates from files,
    render them with variables, and extract template metadata and requirements.
    It implements a singleton pattern for the Jinja2 environment to ensure
    consistent template loading across the application.

    Attributes:
        _env: Class-level singleton instance of Jinja2 Environment

    Example:
        # Render a prompt template with variables
        prompt = PromptManager.get_prompt("greeting", name="Alice")

        # Get template metadata and required variables
        info = PromptManager.get_template_info("greeting")
    """

    _env = None

    @classmethod
    def _get_env(cls, templates_dir="prompts") -> Environment:
        """Gets or creates the Jinja2 environment singleton.

        Args:
            templates_dir: Directory name containing prompt templates, relative to app/

        Returns:
            Configured Jinja2 Environment instance

        Note:
            Uses StrictUndefined to raise errors for undefined variables,
            helping catch template issues early.
        """
        templates_dir = Path(__file__).parent.parent / templates_dir
        if cls._env is None:
            cls._env = Environment(
                loader=FileSystemLoader(templates_dir),
                undefined=StrictUndefined,
            )
        return cls._env

    @staticmethod
    def get_prompt(template: str, **kwargs) -> str:
        """Loads and renders a prompt template with provided variables.

        Args:
            template: Name of the template file (without .j2 extension)
            **kwargs: Variables to use in template rendering

        Returns:
            Rendered template string

        Raises:
            ValueError: If template rendering fails
            FileNotFoundError: If template file doesn't exist
        """
        env = PromptManager._get_env()
        template_path = f"{template}.j2"
        with open(env.loader.get_source(env, template_path)[1]) as file:
            post = frontmatter.load(file)

        template = env.from_string(post.content)
        try:
            return template.render(**kwargs)
        except TemplateError as e:
            raise ValueError(f"Error rendering template: {str(e)}")

    @staticmethod
    def get_template_info(template: str) -> dict:
        """Extracts metadata and variable requirements from a template.

        Args:
            template: Name of the template file (without .j2 extension)

        Returns:
            Dictionary containing:
                - name: Template name
                - description: Template description from frontmatter
                - author: Template author from frontmatter
                - variables: List of required template variables
                - frontmatter: Raw frontmatter metadata dictionary

        Raises:
            FileNotFoundError: If template file doesn't exist
        """
        env = PromptManager._get_env()
        template_path = f"{template}.j2"
        with open(env.loader.get_source(env, template_path)[1]) as file:
            post = frontmatter.load(file)

        ast = env.parse(post.content)
        variables = meta.find_undeclared_variables(ast)

        return {
            "name": template,
            "description": post.metadata.get("description", "No description provided"),
            "author": post.metadata.get("author", "Unknown"),
            "variables": list(variables),
            "frontmatter": post.metadata,
        }
