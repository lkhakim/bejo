import os
import re
import yaml
import logging

logger = logging.getLogger("bejo.skill")

SKILLS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills")


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except Exception as e:
        logger.warning(f"Failed to parse YAML frontmatter: {e}")
        meta = {}
    return meta, m.group(2).strip()


class Skill:
    def __init__(self, name: str, description: str, tags: list[str],
                 tools: list[str], markdown: str, filepath: str):
        self.name = name
        self.description = description
        self.tags = tags or []
        self.tools = tools or []
        self.markdown = markdown
        self.filepath = filepath

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "tags": self.tags,
            "tools": self.tools,
        }


class SkillManager:
    def __init__(self, skills_dir: str = None):
        self.skills_dir = skills_dir or SKILLS_DIR
        self._skills: dict[str, Skill] = {}
        self._load()

    def _load(self):
        if not os.path.isdir(self.skills_dir):
            logger.warning(f"Skills directory not found: {self.skills_dir}")
            return
        for fname in os.listdir(self.skills_dir):
            if not fname.endswith(".md"):
                continue
            fpath = os.path.join(self.skills_dir, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    raw = f.read()
                meta, body = _parse_frontmatter(raw)
                name = meta.get("name", fname.replace(".md", ""))
                description = meta.get("description", "")
                tags = meta.get("tags", [])
                allowed = meta.get("allowed-tools", "")
                tools = [t.strip() for t in allowed.split(",") if t.strip()]
                skill = Skill(
                    name=name, description=description, tags=tags,
                    tools=tools, markdown=body, filepath=fpath,
                )
                self._skills[name] = skill
            except Exception as e:
                logger.warning(f"Failed to load skill {fname}: {e}")
        logger.info(f"Loaded {len(self._skills)} skills from {self.skills_dir}")

    def list_skills(self) -> list[Skill]:
        return list(self._skills.values())

    def get_skill(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def skill_names(self) -> list[str]:
        return sorted(self._skills.keys())

    def to_system_prompt(self) -> str:
        if not self._skills:
            return ""
        lines = ["SKILL YANG TERSEDIA:"]
        for name, skill in sorted(self._skills.items()):
            lines.append(f"- {name}: {skill.description}")
            if skill.tools:
                lines.append(f"  Tools: {', '.join(skill.tools)}")
        return "\n".join(lines)
