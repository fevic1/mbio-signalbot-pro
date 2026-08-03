from pathlib import Path

content = r'''PASTE_THE_MARKDOWN_HERE_EXACTLY'''

Path(".aios/governance/branching-strategy.md").write_text(
    content,
    encoding="utf-8",
)

print("✓ Updated .aios/governance/branching-strategy.md")
