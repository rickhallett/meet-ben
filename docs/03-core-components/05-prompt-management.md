# Prompt Management

The GenAI Launchpad uses a prompt management system based on Jinja2 templating and frontmatter metadata. This approach provides a clean separation between prompt logic and content while enabling powerful template features.

## Why Jinja Templates?

We chose Jinja templating for several key reasons:

1. **Dynamic Content**: Jinja's powerful templating features allow for:
   - Conditional prompt sections
   - Loop-based content generation
   - Variable interpolation
   - Template inheritance and reuse

2. **Separation of Concerns**: Templates separate:
   - Prompt structure (template)
   - Dynamic content (variables)
   - Metadata (frontmatter)

3. **Validation and Type Safety**: When combined with Pydantic models:
   - Template variables can be validated
   - Type hints provide better IDE support
   - Runtime validation ensures data correctness

## Prompt Structure

Prompts are stored as `.j2` files with frontmatter metadata:

```yaml
---
name: ticket_analysis
description: Analyzes customer support tickets for intent and urgency
author: AI Team
version: 1.0
---
You are a customer support analyst. Analyze the following ticket:

Sender: {{ sender }}
Subject: {{ subject }}

Content:
{{ body }}

Provide a structured analysis including:
1. Customer intent
2. Urgency level
3. Required actions

{% if context %}
Consider this additional context:
{% for item in context %}
- {{ item }}
{% endfor %}
{% endif %}
```

## Using the Prompt Manager

### Basic Usage

```python
from services.prompt_loader import PromptManager

# Load and render a prompt
prompt = PromptManager.get_prompt(
    "ticket_analysis",
    sender="customer@example.com",
    subject="Urgent: Login Issue",
    body="Cannot access my account...",
    context=["Previous ticket: Password reset requested"]
)
```

### Getting Template Information

```python
# Get template metadata and requirements
info = PromptManager.get_template_info("ticket_analysis")
print(info)
# {
#     "name": "ticket_analysis",
#     "description": "Analyzes customer support tickets...",
#     "author": "AI Team",
#     "variables": ["sender", "subject", "body", "context"],
#     "frontmatter": {...}
# }
```

## Integration with LLM Nodes

The prompt management system integrates seamlessly with LLM nodes:

```python
class AnalyzeTicket(LLMNode):
    def create_completion(self, context: ContextModel) -> ResponseModel:
        # Load prompt template
        prompt = PromptManager.get_prompt(
            "ticket_analysis",
            pipeline="support",
            sender=context.sender,
            subject=context.subject,
            body=context.body
        )
        
        # Use in LLM completion
        return self.llm.create_completion(
            response_model=self.ResponseModel,
            messages=[
                {"role": "system", "content": prompt}
            ]
        )
```

## Prompt Organization

Prompts are organized in a dedicated directory structure:

```
app/
└── prompts/
    ├── support/
    │   ├── ticket_analysis.j2
    │   └── response_template.j2
    ├── content/
    │   ├── summarize.j2
    │   └── analyze.j2
    └── shared/
        └── common_instructions.j2
```

## Advanced Features

### Template Inheritance

```jinja
{# base_prompt.j2 #}
{% block system_instruction %}{% endblock %}

{% block content %}{% endblock %}

{% block response_format %}{% endblock %}

{# specific_prompt.j2 #}
{% extends "base_prompt.j2" %}

{% block system_instruction %}
You are an AI assistant specialized in...
{% endblock %}

{% block content %}
Analyze the following: {{ content }}
{% endblock %}
```

### Conditional Logic

```jinja
{% if confidence_required %}
Please provide confidence scores for each analysis point.
{% endif %}

{% if language != "english" %}
Respond in {{ language }}.
{% endif %}
```

### Loops and Data Structures

```jinja
Consider the following context:
{% for item in context_items %}
{{ loop.index }}. {{ item.title }}
   - Relevance: {{ item.relevance }}
   - Source: {{ item.source }}
{% endfor %}
```

## Best Practices

1. **Version Control**:
   - Keep prompts in version control
   - Use frontmatter for versioning metadata
   - Document changes in prompt files

2. **Template Organization**:
   - Group related prompts in subdirectories
   - Use clear, descriptive filenames
   - Include usage examples in frontmatter

3. **Variable Management**:
   - Document required variables
   - Provide default values where appropriate
   - Use type hints in documentation

4. **Error Handling**:
   ```python
   try:
       prompt = PromptManager.get_prompt("template_name", **vars)
   except TemplateError as e:
       logger.error(f"Template error: {e}")
       # Handle gracefully
   ```

## Security Considerations

1. **Input Validation**:
   - All template variables are escaped by default
   - Use StrictUndefined to catch undefined variables
   - Validate input data before rendering

2. **Access Control**:
   - Store sensitive prompts separately
   - Use environment variables for sensitive data
   - Implement prompt access controls if needed

For more information on Jinja templating in LLM applications, see the [Instructor documentation on Jinja integration](https://python.useinstructor.com/blog/2024/09/19/instructor-proposal-integrating-jinja-templating/).