from lib.rules.openspec_paths import change_dir, delta_change_dir, is_archived


def test_change_dir():
    assert change_dir("openspec/changes/add-x/tasks.md") == "openspec/changes/add-x/"
    assert change_dir("pkg/openspec/changes/archive/2026-01-01-add-x/tasks.md") == \
        "pkg/openspec/changes/archive/2026-01-01-add-x/"


def test_is_archived():
    assert is_archived("openspec/changes/archive/2026-01-01-x/tasks.md")
    assert is_archived("OpenSpec/changes/Archive/x/tasks.md")
    assert is_archived("openspec/archive/x/tasks.md")
    assert not is_archived("openspec/changes/archiver-tool/tasks.md")


def test_delta_change_dir():
    assert delta_change_dir("openspec/changes/x/specs/auth/spec.md") == "openspec/changes/x/"
    assert delta_change_dir("openspec/changes/archive/d-x/specs/a/spec.md") == "openspec/changes/archive/d-x/"
    # A living spec maps to openspec/, which is never a change folder.
    assert delta_change_dir("openspec/specs/auth/spec.md") == "openspec/"
    assert delta_change_dir("spec.md") == ""
