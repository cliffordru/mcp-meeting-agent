"""Tests for the MeetingNotesFormatter class."""

import unittest
from app.formatters.meeting_notes_formatter import MeetingNotesFormatter
from app.schemas.tech_trivia import TechTriviaQuestion
from app.schemas.fun_facts import FunFact


class TestMeetingNotesFormatter(unittest.TestCase):
    """Test cases for MeetingNotesFormatter."""

    def setUp(self):
        """Set up test fixtures."""
        self.trivia_question = TechTriviaQuestion(
            category="Science: Computers",
            type="multiple",
            difficulty="medium",
            question="What is Python?",
            correct_answer="Programming language",
            incorrect_answers=["Snake", "Game", "Database"]
        )
        
        self.fun_fact = FunFact(
            id="123",
            text="Python was named after Monty Python",
            source="Test Source",
            source_url="https://test.com",
            language="en",
            permalink="https://test.com/fact/123"
        )
        
        self.trending_repos = [
            {
                'name': 'repo1',
                'description': 'Test repository 1',
                'language': 'Python',
                'stars': '100',
                'url': 'https://github.com/repo1'
            },
            {
                'name': 'repo2',
                'description': 'Test repository 2',
                'language': 'JavaScript',
                'stars': '50',
                'url': 'https://github.com/repo2'
            },
            {
                'name': 'repo3',
                'description': 'Test repository 3',
                'language': 'TypeScript',
                'stars': '75',
                'url': 'https://github.com/repo3'
            }
        ]

    def test_format_meeting_notes_success(self):
        """Test successful formatting of meeting notes."""
        result = MeetingNotesFormatter.format_meeting_notes(
            self.trivia_question, self.fun_fact, self.trending_repos
        )
        
        # Check that the result contains expected sections
        self.assertIn("Meeting Notes for Host", result)
        self.assertIn("Ice Breaker - Tech Trivia:", result)
        self.assertIn("Fun Fact to Share:", result)
        self.assertIn("Trending Tech Topics:", result)
        
        # Check that the content is included
        self.assertIn("What is Python?", result)
        self.assertIn("Programming language", result)
        self.assertIn("Python was named after Monty Python", result)
        self.assertIn("repo1", result)
        self.assertIn("Test repository 1", result)
        self.assertIn("https://github.com/repo1", result)

    def test_format_meeting_notes_with_empty_repos(self):
        """Test formatting with empty trending repositories."""
        empty_repos = []
        result = MeetingNotesFormatter.format_meeting_notes(
            self.trivia_question, self.fun_fact, empty_repos
        )
        
        self.assertIn("Meeting Notes for Host", result)
        self.assertIn("What is Python?", result)
        self.assertIn("Python was named after Monty Python", result)

    def test_format_meeting_notes_with_string_repos(self):
        """Test formatting with string-based repositories (fallback format)."""
        string_repos = ["repo1", "repo2", "repo3"]
        result = MeetingNotesFormatter.format_meeting_notes(
            self.trivia_question, self.fun_fact, string_repos
        )
        
        self.assertIn("Meeting Notes for Host", result)
        self.assertIn("• repo1", result)
        self.assertIn("• repo2", result)
        self.assertIn("• repo3", result)

    def test_format_meeting_notes_limits_to_three_repos(self):
        """Test that only the first 3 repositories are included."""
        many_repos = [
            {'name': f'repo{i}', 'description': f'desc{i}', 'language': 'Python', 'stars': '10', 'url': f'https://github.com/repo{i}'}
            for i in range(5)
        ]
        
        result = MeetingNotesFormatter.format_meeting_notes(
            self.trivia_question, self.fun_fact, many_repos
        )
        
        # Should include first 3 repos
        self.assertIn("repo0", result)
        self.assertIn("repo1", result)
        self.assertIn("repo2", result)
        
        # Should not include repos beyond the first 3
        self.assertNotIn("repo3", result)
        self.assertNotIn("repo4", result)


if __name__ == '__main__':
    unittest.main()
