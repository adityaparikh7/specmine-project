import pytest

from lib.rules.intent_rules import classify, parse_checkbox, strip_lead

CASES = [
    # (task text, code path, intent, move role)
    ("2.2 Create `apps/api/src/lib/auth.ts` with the auth instance", "apps/api/src/lib/auth.ts", "create", ""),
    ("**1.1** Scaffold `src/app.ts`", "src/app.ts", "create", ""),
    ("Write `tests/login.test.ts` covering the happy path", "tests/login.test.ts", "create", ""),
    ("Add `src/util/date.ts`", "src/util/date.ts", "create", ""),
    ("Add COMMAND_IDS constant to `src/core/tool-detection.ts`", "src/core/tool-detection.ts", "modify", ""),
    ("Add LoadAgentFromDir tests in `internal/prompt/loader_test.go`", "internal/prompt/loader_test.go", "modify", ""),
    ("Update `apps/web/src/AppLayout.tsx` to fetch shelves", "apps/web/src/AppLayout.tsx", "modify", ""),
    ("GREEN: Fix the parser in `src/parse.rs`", "src/parse.rs", "modify", ""),
    ("Delete `webcompy/cli/server_config.py` (merged)", "webcompy/cli/server_config.py", "delete", ""),
    ("Remove `db_path` case from `internal/cli/state_update.go`", "internal/cli/state_update.go", "modify", ""),
    ("Move `vite.config.ts` → `packages/client/vite.config.ts`", "vite.config.ts", "move", "source"),
    ("Move `vite.config.ts` → `packages/client/vite.config.ts`", "packages/client/vite.config.ts", "move", "target"),
    ("Move helpers from `src/cli/main.js` into `src/git/index.js`", "src/git/index.js", "move", "target"),
    ("`back-target.test.ts` passes unchanged", "back-target.test.ts", "other", ""),
    ("Read `app/services/handler.rb`", "app/services/handler.rb", "other", ""),
    # the file named first, then what to do with it
    ("In `src/core/registry.ts`, add the new tool", "src/core/registry.ts", "modify", ""),
    ("`internal/handler/coverage.go`: parse the body and cap entries", "internal/handler/coverage.go", "other", ""),
    ("`src/routes.ts`: update the login route", "src/routes.ts", "modify", ""),
    ("`src/new_module.py` — new file exporting helpers", "src/new_module.py", "create", ""),
    ("`src/a.ts`: create with the parser", "src/a.ts", "create", ""),
    ("In `src/components/`: create `Card.tsx`", "Card.tsx", "create", ""),
    ("3.1 In `src/routes/file-routes.ts`, parse `detect` from the query", "src/routes/file-routes.ts", "modify", ""),
    ("2.1 In `App.tsx` `handleSend`, after sending, set state", "App.tsx", "modify", ""),
    ("4.1 在 `e2e/helpers.go` 的 `setup` 函数中，补加调用", "e2e/helpers.go", "modify", ""),
    ("1.6 寫 `test_multi_open_detect.py`：fake proc", "test_multi_open_detect.py", "create", ""),
    # other languages
    ("1.2 创建 `agent/middlewares/__init__.py` 文件", "agent/middlewares/__init__.py", "create", ""),
    ("在 `agent/capabilities.py` 中添加 deprecated 导入别名", "agent/capabilities.py", "modify", ""),
    ("更新 `agent/runtime_agent.py` 中的导入路径", "agent/runtime_agent.py", "modify", ""),
    ("删除 `old/legacy.py`", "old/legacy.py", "delete", ""),
    ("`src/foo.ts` を作成する", "src/foo.ts", "create", ""),
    ("`src/foo.ts` を削除", "src/foo.ts", "delete", ""),
    ("Crear `src/main.py` con la configuración", "src/main.py", "create", ""),
    ("Atualizar `src/app.ts`", "src/app.ts", "modify", ""),
    ("`src/x.ts` erstellen", "src/x.ts", "create", ""),
]


@pytest.mark.parametrize("text,path,intent,role", CASES)
def test_classify(text, path, intent, role):
    got_intent, _, got_role = classify(text, path)
    assert (got_intent, got_role) == (intent, role)


def test_parse_checkbox():
    assert parse_checkbox("- [x] 1.1 Create `a.ts`") == (True, "1.1 Create `a.ts`")
    assert parse_checkbox("  * [ ] Update b") == (False, "Update b")
    assert parse_checkbox("1. [X] Done") == (True, "Done")
    assert parse_checkbox("- plain bullet") is None


def test_strip_lead():
    assert strip_lead("**2.3** Create `x`").startswith("Create")
    assert strip_lead("T001 [P] Create x").startswith("Create")
    assert strip_lead("RED: Write test").startswith("Write")
