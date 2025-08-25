"""
Meeting-related prompt templates.
"""


class MeetingPrompts:
    """
    A class containing prompt templates for meeting-related tasks.
    """
    
    @staticmethod
    def format_meeting_info_prompt(
        trivia_question: str,
        trivia_answer: str,
        fun_fact: str,
        trending_repos_text: str
    ) -> str:
        """
        Creates a prompt for formatting meeting information using LLM.
        
        Args:
            trivia_question: The tech trivia question
            trivia_answer: The correct answer to the trivia question
            fun_fact: The fun fact to share
            trending_repos_text: Formatted trending repositories text
            
        Returns:
            Formatted prompt string for LLM
        """
        return f"""
        Create meeting notes for the host to use at the start of a meeting. Include the following information in a concise, professional format:

        Tech Trivia Question: {trivia_question}
        Tech Trivia Answer: {trivia_answer}
        Fun Fact: {fun_fact}
        Trending GitHub Repositories: {trending_repos_text}
        
        Format this as meeting notes that a host can quickly reference to:
        1. Break the ice with the trivia question
        2. Share an interesting fun fact
        3. Mention trending tech topics from GitHub with their descriptions and links
        
        Keep it concise and professional, suitable for a business meeting context.
        """
