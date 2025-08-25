"""Tests for the RepositoryFormatter class."""

import unittest
from app.formatters.repository_formatter import RepositoryFormatter


class TestRepositoryFormatter(unittest.TestCase):
    """Test cases for RepositoryFormatter."""

    def setUp(self):
        """Set up test fixtures."""
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

    def test_format_trending_repos_for_llm_success(self):
        """Test successful formatting for LLM consumption."""
        result = RepositoryFormatter.format_trending_repos_for_llm(self.trending_repos)
        
        # Check that the result contains expected formatting
        self.assertIn("**repo1**", result)
        self.assertIn("Test repository 1", result)
        self.assertIn("(Python)", result)
        self.assertIn("⭐ 100", result)
        self.assertIn("https://github.com/repo1", result)
        self.assertIn("**repo2**", result)
        self.assertIn("**repo3**", result)

    def test_format_trending_repos_for_notes_success(self):
        """Test successful formatting for meeting notes."""
        result = RepositoryFormatter.format_trending_repos_for_notes(self.trending_repos)
        
        # Check that the result contains expected formatting
        self.assertIn("• repo1", result)
        self.assertIn("Test repository 1", result)
        self.assertIn("(Python)", result)
        self.assertIn("⭐ 100", result)
        self.assertIn("https://github.com/repo1", result)
        self.assertIn("• repo2", result)
        self.assertIn("• repo3", result)

    def test_format_trending_repos_limits_to_three(self):
        """Test that only the first 3 repositories are included."""
        many_repos = [
            {'name': f'repo{i}', 'description': f'desc{i}', 'language': 'Python', 'stars': '10', 'url': f'https://github.com/repo{i}'}
            for i in range(5)
        ]
        
        llm_result = RepositoryFormatter.format_trending_repos_for_llm(many_repos)
        notes_result = RepositoryFormatter.format_trending_repos_for_notes(many_repos)
        
        # Should include first 3 repos
        self.assertIn("repo0", llm_result)
        self.assertIn("repo1", llm_result)
        self.assertIn("repo2", llm_result)
        self.assertIn("repo0", notes_result)
        self.assertIn("repo1", notes_result)
        self.assertIn("repo2", notes_result)
        
        # Should not include repos beyond the first 3
        self.assertNotIn("repo3", llm_result)
        self.assertNotIn("repo4", llm_result)
        self.assertNotIn("repo3", notes_result)
        self.assertNotIn("repo4", notes_result)

    def test_format_trending_repos_with_string_repos(self):
        """Test formatting with string-based repositories (fallback format)."""
        string_repos = ["repo1", "repo2", "repo3"]
        
        llm_result = RepositoryFormatter.format_trending_repos_for_llm(string_repos)
        notes_result = RepositoryFormatter.format_trending_repos_for_notes(string_repos)
        
        self.assertIn("repo1", llm_result)
        self.assertIn("repo2", llm_result)
        self.assertIn("repo3", llm_result)
        self.assertIn("• repo1", notes_result)
        self.assertIn("• repo2", notes_result)
        self.assertIn("• repo3", notes_result)

    def test_format_trending_repos_with_empty_repos(self):
        """Test formatting with empty repository list."""
        empty_repos = []
        
        llm_result = RepositoryFormatter.format_trending_repos_for_llm(empty_repos)
        notes_result = RepositoryFormatter.format_trending_repos_for_notes(empty_repos)
        
        expected_message = "No trending repositories available at the moment."
        self.assertEqual(llm_result, expected_message)
        self.assertEqual(notes_result, expected_message)


if __name__ == '__main__':
    unittest.main()
