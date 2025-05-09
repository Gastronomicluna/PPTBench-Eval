SCORING_CRITERIA = """
0 = Very Poor: No meaningful content, or completely unreadable/confusing
1 = Poor: Message unclear, poor design, serious issues with layout or content
2 = Fair: Basic message is present but lacks clarity, coherence, or visual polish
3 = Good: Message is clear, design is acceptable, some minor improvements needed
4 = Very Good: Strong clarity and design, effective visual support for the message
5 = Excellent: Highly professional, well-balanced, impactful, and visually engaging
"""

RESPONSE_FORMAT = """
Response Format:
Reasoning:
- Clarity of Message: ...
- Visual Design & Readability: ...
- Content Appropriateness: ...
- Audience Engagement: ...
- Professionalism & Consistency: ...
Score: [[x]]  # Replace x with a number from 0 to 5 (e.g., [[3]])
"""

PROMPT_TEMPLATE = """
You are an expert in evaluating the quality of PowerPoint slides. Your task is to assess the quality of the slides based on the provided criteria.
Please provide a score from 0 to 5 for each slide, with the score formatted as [[x]] for easy parsing. Also include a brief explanation of your reasoning.

Use the following scoring criteria:
{scoring_criteria}

The screenshot of the slide is provided below. Please evaluate the slide and provide your score.
Your response must follow the format below:
{response_format}

Note you must return the score in the format [[x]] where x is a integer from 0 to 5.
""".format(
    scoring_criteria=SCORING_CRITERIA,
    response_format=RESPONSE_FORMAT
)
