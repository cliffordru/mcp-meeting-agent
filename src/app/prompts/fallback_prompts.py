"""
Fallback prompts for when external APIs fail.
Uses LangChain's ChatPromptTemplate for consistent prompt management.
"""
from langchain_core.prompts import ChatPromptTemplate

# Tech trivia fallback prompt
TECH_TRIVIA_FALLBACK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that generates engaging technology trivia questions for software development team meetings."),
    ("user", "Generate a technology trivia question and answer that would be engaging for a software development team meeting. Make it relevant to current tech trends and interesting for developers. Format your response as:\n\nQuestion: [Your question here]\nAnswer: [Your answer here]")
])

# Fun fact fallback prompt
FUN_FACT_FALLBACK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that generates interesting and relevant fun facts for team meetings."),
    ("user", "Generate an interesting fun fact that would be engaging for a software development team meeting. Make it relevant to technology, programming, or general knowledge that developers would find interesting. Start with 'Did you know?' and keep it concise.")
])

# Trending repos fallback prompt
TRENDING_REPOS_FALLBACK_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant that provides information about trending technology repositories and projects."),
    ("user", "Provide information about 3 current trending technology repositories or projects that would be interesting for a software development team. Include the repository name, a brief description, and why it's relevant. Format as a bulleted list.")
])
