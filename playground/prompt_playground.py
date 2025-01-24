import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "app"))

from services.prompt_loader import PromptManager  # noqa: E402

"""
This playground is used to test the PromptManager and the prompts themselves.
"""
ask_question_prompt = PromptManager.get_prompt(
    "ask_question", knowledge_entries=["hello", "world"], questions=["what is the meaning of life?"]
)
print(ask_question_prompt)

# # --------------------------------------------------------------
# # Test support prompt
# # --------------------------------------------------------------

# support_prompt = PromptManager.get_prompt(
#     "ticket_analysis", pipeline="support", ticket={}
# )
# print(support_prompt)

# # --------------------------------------------------------------
# # Test helpdesk prompt
# # --------------------------------------------------------------

# helpdesk_prompt = PromptManager.get_prompt(
#     "ticket_analysis", pipeline="helpdesk", ticket={}
# )
# print(helpdesk_prompt)

# # --------------------------------------------------------------
# # Test knowledge gap check prompt
# # --------------------------------------------------------------

