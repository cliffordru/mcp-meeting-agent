"""Tests for the MeetingPrompts class."""

import unittest
from app.prompts.meeting_prompts import MeetingPrompts


class TestMeetingPrompts(unittest.TestCase):
    """Test cases for MeetingPrompts."""

    def test_format_meeting_info_prompt_success(self):
        """Test successful prompt generation."""
        trivia_question = "What is Python?"
        trivia_answer = "Programming language"
        fun_fact = "Python was named after Monty Python"
        trending_repos_text = "**repo1** - Test repository (Python) ⭐ 100 - https://github.com/repo1"
        
        result = MeetingPrompts.format_meeting_info_prompt(
            trivia_question, trivia_answer, fun_fact, trending_repos_text
        )
        
        # Check that the prompt contains all the input data
        self.assertIn("What is Python?", result)
        self.assertIn("Programming language", result)
        self.assertIn("Python was named after Monty Python", result)
        self.assertIn("**repo1** - Test repository (Python) ⭐ 100 - https://github.com/repo1", result)
        
        # Check that the prompt contains expected instructions
        self.assertIn("Create meeting notes for the host", result)
        self.assertIn("Break the ice with the trivia question", result)
        self.assertIn("Share an interesting fun fact", result)
        self.assertIn("Mention trending tech topics", result)
        self.assertIn("concise and professional", result)

    def test_format_meeting_info_prompt_with_empty_inputs(self):
        """Test prompt generation with empty inputs."""
        result = MeetingPrompts.format_meeting_info_prompt("", "", "", "")
        
        # Should still generate a valid prompt structure
        self.assertIn("Create meeting notes for the host", result)
        self.assertIn("Tech Trivia Question:", result)
        self.assertIn("Tech Trivia Answer:", result)
        self.assertIn("Fun Fact:", result)
        self.assertIn("Trending GitHub Repositories:", result)

    def test_format_meeting_info_prompt_with_special_characters(self):
        """Test prompt generation with special characters."""
        trivia_question = "What is the & symbol used for?"
        trivia_answer = "Bitwise AND operator"
        fun_fact = "The & symbol is called an ampersand"
        trending_repos_text = "**test/repo** - Test & demo (C++) ⭐ 50"
        
        result = MeetingPrompts.format_meeting_info_prompt(
            trivia_question, trivia_answer, fun_fact, trending_repos_text
        )
        
        # Check that special characters are preserved
        self.assertIn("What is the & symbol used for?", result)
        self.assertIn("Bitwise AND operator", result)
        self.assertIn("The & symbol is called an ampersand", result)
        self.assertIn("**test/repo** - Test & demo (C++) ⭐ 50", result)


if __name__ == '__main__':
    unittest.main()
