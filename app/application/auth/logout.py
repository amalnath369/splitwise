from __future__ import annotations


class LogoutUseCase:
    """
    JWT is stateless — logout is handled client-side by discarding the token.
    This use case exists as a placeholder; the router returns 200 with no body.
    Production implementation would add the token to a Redis blacklist.
    """

    async def execute(self) -> None:
        pass
