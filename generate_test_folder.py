import json
import os
import random
import string


ROOT = "test_project"


def random_text(lines: int = 5) -> str:
    words = ["alpha", "beta", "gamma", "delta", "epsilon", "zeta", "lambda", "sigma"]
    return "\n".join(
        " ".join(random.choices(words, k=random.randint(4, 10)))
        for _ in range(lines)
    )


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def generate() -> None:
    # Version file so BackupManager can detect it
    write(
        os.path.join(ROOT, "package.json"),
        json.dumps({"name": "test-project", "version": "2.7.1"}, indent=2),
    )

    write(os.path.join(ROOT, "README.md"), "# Test Project\n\nGenerated for backup testing.\n")

    # src/
    for name in ("main.py", "utils.py", "models.py"):
        write(os.path.join(ROOT, "src", name), f'# {name}\n\n{random_text(8)}\n')

    # src/assets/
    for name in ("style.css", "index.html"):
        write(os.path.join(ROOT, "src", "assets", name), random_text(4))

    # data/
    for i in range(1, 4):
        write(os.path.join(ROOT, "data", f"record_{i:03}.csv"), "id,value\n" + "\n".join(
            f"{j},{random.randint(0, 999)}" for j in range(1, 6)
        ))

    # docs/
    write(os.path.join(ROOT, "docs", "spec.txt"), random_text(12))
    write(os.path.join(ROOT, "docs", "changelog.txt"), "v2.7.1 - initial release\n")

    # nested subfolder
    write(os.path.join(ROOT, "src", "lib", "core", "engine.py"), f'# engine\n\n{random_text(6)}\n')

    total = sum(len(files) for _, _, files in os.walk(ROOT))
    print(f"Test folder '{ROOT}' created with {total} files.")


if __name__ == "__main__":
    generate()
