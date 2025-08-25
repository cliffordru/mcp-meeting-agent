"""
Repository formatting utilities.
"""
from typing import List, Dict


class RepositoryFormatter:
    """
    A class responsible for formatting repository information.
    """
    
    @staticmethod
    def format_trending_repos_for_llm(trending_repos: List[Dict[str, str]]) -> str:
        """
        Formats trending repositories for LLM consumption with markdown formatting.
        
        Args:
            trending_repos: List of repository dictionaries
            
        Returns:
            Formatted string for LLM prompt
        """
        if not trending_repos:
            return "No trending repositories available at the moment."
            
        trending_repos_formatted = []
        for repo in trending_repos[:3]:  # Take top 3
            if isinstance(repo, dict):
                name = repo.get('name', 'Unknown')
                description = repo.get('description', '')
                url = repo.get('url', '')
                language = repo.get('language', '')
                stars = repo.get('stars', '')
                
                repo_info = f"**{name}**"
                if description:
                    repo_info += f" - {description}"
                if language:
                    repo_info += f" ({language})"
                if stars and stars != '0':
                    repo_info += f" ⭐ {stars}"
                if url:
                    repo_info += f" - {url}"
                
                trending_repos_formatted.append(repo_info)
            else:
                # Fallback for old string format
                trending_repos_formatted.append(str(repo))
        
        return "\n   - ".join(trending_repos_formatted)
    
    @staticmethod
    def format_trending_repos_for_notes(trending_repos: List[Dict[str, str]]) -> str:
        """
        Formats trending repositories for meeting notes with bullet points.
        
        Args:
            trending_repos: List of repository dictionaries
            
        Returns:
            Formatted string for meeting notes
        """
        if not trending_repos:
            return "No trending repositories available at the moment."
            
        trending_repos_formatted = []
        for repo in trending_repos[:3]:  # Take top 3
            if isinstance(repo, dict):
                name = repo.get('name', 'Unknown')
                description = repo.get('description', '')
                url = repo.get('url', '')
                language = repo.get('language', '')
                stars = repo.get('stars', '')
                
                repo_info = f"• {name}"
                if description:
                    repo_info += f" - {description}"
                if language:
                    repo_info += f" ({language})"
                if stars and stars != '0':
                    repo_info += f" ⭐ {stars}"
                if url:
                    repo_info += f" - {url}"
                
                trending_repos_formatted.append(repo_info)
            else:
                # Fallback for old string format
                trending_repos_formatted.append(f"• {str(repo)}")
        
        return "\n".join(trending_repos_formatted)
