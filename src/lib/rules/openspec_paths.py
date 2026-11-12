"""Where an OpenSpec file sits: which change it belongs to, and whether that change is archived.

A change is the folder that holds its tasks.md, for example
    openspec/changes/add-login/                         (in progress)
    openspec/changes/archive/2026-04-25-add-login/      (archived)
Layouts vary (OpenSpec/changes/, openspec/archive/, monorepo prefixes), so we
work with folders rather than one fixed prefix.
"""
import re


def change_dir(path):
    """The folder of a tasks.md or proposal.md, with a trailing slash."""
    return path.rsplit("/", 1)[0] + "/" if "/" in path else ""


def is_archived(path):
    """True when the path has an archive/ folder anywhere in it (any case)."""
    return re.search(r"(^|/)archive/", path, re.IGNORECASE) is not None


def delta_change_dir(path):
    """The change folder of a spec delta: everything before its first '/specs/'.

    openspec/changes/add-login/specs/auth/spec.md -> openspec/changes/add-login/
    A living spec (openspec/specs/auth/spec.md) gives 'openspec/', which never
    matches a change folder, so it simply finds no change.
    """
    match = re.match(r"^(.*?/)specs/", path)
    return match.group(1) if match else ""
