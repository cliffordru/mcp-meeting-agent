"""
Meeting notes formatting utilities.
"""
from typing import List, Dict
from ..schemas.tech_trivia import TechTriviaQuestion
from ..schemas.fun_facts import FunFact
from .repository_formatter import RepositoryFormatter


class MeetingNotesFormatter:
    """A class responsible for formatting meeting notes from various data sources."""

    @staticmethod
    def format_meeting_notes(
        trivia_question: TechTriviaQuestion,
        fun_fact: FunFact,
        trending_repos: List[Dict[str, str]]
    ) -> str:
        """
        Formats meeting notes from trivia, fun fact, and trending repositories.

        Args:
            trivia_question: The tech trivia question and answer
            fun_fact: The fun fact to share
            trending_repos: List of trending repository dictionaries

        Returns:
            Formatted meeting notes as a string
        """
        trending_repos_text = RepositoryFormatter.format_trending_repos_for_notes(trending_repos)

        meeting_notes = [
            "Meeting Notes for Host",
            "",
            "Ice Breaker - Tech Trivia:",
            f"Q: {trivia_question.question}",
            f"A: {trivia_question.correct_answer}",
            "",
            "Fun Fact to Share:",
            fun_fact.text,
            "",
            "Trending Tech Topics:",
            trending_repos_text,
            "",
            "Use these notes to:",
            "1. Start with the trivia question to engage the team",
            "2. Share the fun fact for a light moment",
            "3. Mention trending repositories as conversation starters"
        ]

        return "\n".join(meeting_notes)
