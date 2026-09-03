"""Repository paths shared by the application features."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ProjectPaths:
    root: Path
    content: Path
    research: Path
    output: Path
    images: Path
    shot_labels: Path
    downloads: Path
    game_list: Path
    manifest: Path
    schema: Path
    research_prompt_template: Path
    format_prompt_template: Path

    @classmethod
    def from_root(cls, root: Path) -> "ProjectPaths":
        content = root / "content"
        return cls(
            root=root,
            content=content,
            research=content / "research",
            output=root / "output",
            images=root / "images",
            shot_labels=root / "shot-labels",
            downloads=Path.home() / "Downloads",
            game_list=content / "list_of_games.txt",
            manifest=root / "pins.yaml",
            schema=root / "schema" / "game.schema.json",
            research_prompt_template=root / "prompts" / "research-game.md",
            format_prompt_template=root / "prompts" / "format-game-yaml.md",
        )


PATHS = ProjectPaths.from_root(Path(__file__).resolve().parents[1])

ROOT = PATHS.root
CONTENT = PATHS.content
RESEARCH = PATHS.research
OUTPUT = PATHS.output
IMAGES = PATHS.images
SHOT_LABELS = PATHS.shot_labels
DOWNLOADS = PATHS.downloads
GAME_LIST = PATHS.game_list
MANIFEST = PATHS.manifest
SCHEMA = PATHS.schema
RESEARCH_PROMPT_TEMPLATE = PATHS.research_prompt_template
FORMAT_PROMPT_TEMPLATE = PATHS.format_prompt_template
