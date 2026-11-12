import pytest

from lib.rules.ref_noise import noise_rule

NOISE = {
    "Next.js": "tech_name",
    "node.js": "tech_name",
    ".ts": "bare_extension",
    ".py": "bare_extension",
    "src/**/*.ts": "glob",
    "{a,b}.ts": "glob",
    "7.6.F1.c": "task_number",
    "1.1.c": "task_number",
    "dist/<app>/index.html": "placeholder",
    "https://cdn.example.com/x.js": "url",
}
REAL_FILES = ["App.tsx", ".env", ".gitignore", "next.config.js", "app/[...slug]/page.tsx",
              "src/lib/node.ts", "domain/ui/.../StatusScreen.kt", "v1.2/handler.go", "__init__.py"]


@pytest.mark.parametrize("path,rule", NOISE.items())
def test_noise(path, rule):
    assert noise_rule(path) == rule


@pytest.mark.parametrize("path", REAL_FILES)
def test_real_files_are_kept(path):
    assert noise_rule(path) is None
