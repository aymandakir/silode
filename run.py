from __future__ import annotations

from typing import Optional

import typer
import uvicorn

from app.config import get_settings
from app.engine import engine

cli = typer.Typer(help="Silode CLI")


@cli.command()
def serve(
    host: Optional[str] = typer.Option(default=None, help="Bind host"),
    port: Optional[int] = typer.Option(default=None, help="Bind port"),
    reload: bool = typer.Option(default=False, help="Enable auto-reload"),
) -> None:
    """Start the local API server."""
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=host or settings.host,
        port=port or settings.port,
        reload=reload,
    )


@cli.command()
def prompt(
    text: str = typer.Argument(..., help="Prompt text"),
    model: Optional[str] = typer.Option(default=None, help="Model name"),
) -> None:
    """Run a single prompt locally."""
    settings = get_settings()
    result = engine.generate(
        model_name=model or settings.default_model,
        prompt=text,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
    )
    typer.echo(result.text)


if __name__ == "__main__":
    cli()
