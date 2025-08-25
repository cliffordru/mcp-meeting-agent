"""
An agent responsible for fetching fun facts.
"""
from typing import Optional

from ..services.fun_facts_service import FunFactsService
from ..schemas.fun_facts import FunFact


class FunFactsAgent:
    """
    Wraps the FunFactsService to provide a clean interface for fetching fun facts.
    """

    def __init__(self):
        self._service = FunFactsService()

    async def get_fun_fact(self) -> FunFact:
        """
        Fetches a fun fact.

        Returns:
            A FunFact object.
        """
        fun_fact = await self._service.get_fun_fact()
        return fun_fact