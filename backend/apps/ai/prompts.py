DRAFT_PROMPT = (
    "You are a content creation assistant. Based on the following brief, "
    "generate a compelling headline and description.\n"
    "\n"
    "Brief: {brief}\n"
    "\n"
    "Respond with valid JSON in this format:\n"
    '{{"headline": "...", "description": "..."}}\n'
    "\n"
    "Ensure the headline is attention-grabbing and under 100 characters.\n"
    "The description should be 2-3 sentences that expand on the headline."
)

TRANSLATION_PROMPT = (
    "You are a professional translator. Translate the following content "
    "to {target_language}.\n"
    "\n"
    "Headline: {headline}\n"
    "Description: {description}\n"
    "\n"
    "Respond with valid JSON in this format:\n"
    '{{"headline": "...", "description": "..."}}\n'
    "\n"
    "Preserve the tone and style of the original."
)


def format_draft_prompt(brief: str) -> str:
    return DRAFT_PROMPT.replace("{brief}", brief)


def format_translation_prompt(
    headline: str,
    description: str,
    target_language: str,
) -> str:
    return (
        TRANSLATION_PROMPT
        .replace("{headline}", headline)
        .replace("{description}", description)
        .replace("{target_language}", target_language)
    )
