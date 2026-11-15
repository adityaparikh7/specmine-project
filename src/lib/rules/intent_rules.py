"""Task intent: what a checked task line says to do to the file it names.

    create   the task says to make a new file          ("Create `src/auth.ts`")
    modify   the task says to change an existing file   ("Update `src/routes.ts` to ...")
    delete   the task says to remove the file           ("Delete `old.js`")
    move     the task says to move or rename the file   ("Move `a.ts` to `b.ts`")
    other    no clear verb                              ("`foo.test.ts` passes", "Read `x.rb`")

English uses the LEADING verb of the task (after numbers, bold, backticks and
"LABEL:" prefixes). Nine other languages (zh, ja, ko, es, pt, de, fr, ru, vi)
put the verb in different places, so for them the earliest verb keyword
anywhere in the line wins.

Three context rules fix the commonest misreads:
  - "Add X to `file`" / "Add X in `file`"      -> modify, not create
  - "Remove X from `file`"                     -> modify, not delete
  - "Move `a` to `b`": `a` is the move source (should be gone), `b` the target (should exist)

Kept deliberately small and readable; tests/test_intent_rules.py pins the behaviour.
"""
import re

# --- the checkbox line ------------------------------------------------------
CHECKBOX = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s*\[([ xX])\]\s?(.*)$")
# Leading clutter before the verb: task numbers, bold/italics/backticks, "[P]", "T001", "LABEL:".
LEAD = re.compile(
    r"^(?:\s+|[*_`~]+|\d+(?:\.\d+)*[.):]?(?=[\s*_`])|[A-Z]{1,4}\d{1,4}[.:]?\s|\[[^\]]{1,12}\]\s?"
    r"|\(?[A-Za-z]{2,10}\)?\s*:\s|DONE\s*[—–-]\s*)")

# --- English leading verbs ----------------------------------------------------
EN = {
    "create": "create creates created scaffold scaffolds generate generates introduce introduces new "
              "initialize initialise init bootstrap write writes add adds added",
    "modify": "update updates updated modify modifies modified edit edits change changes fix fixes refactor "
              "refactors extend extends wire wires register registers export exports replace replaces "
              "adjust adjusts integrate integrates enhance enhances improve improves patch patches "
              "rewrite rewrites convert converts tweak rework harden align amend append "
              "inject hook hooks expose exposes import imports",
    "delete": "delete deletes deleted remove removes removed drop drops purge eliminate",
    "move": "move moves moved rename renames renamed relocate relocates migrate migrates",
}
EN_VERB = {verb: intent for intent, words in EN.items() for verb in words.split()}

# --- other languages: keyword -> intent (earliest match wins) -----------------
OTHER = {
    "create": [r"创建", r"新建", r"新增", r"建立", r"添加", r"增加", r"编写", r"撰写", r"撰寫", r"寫", r"写", r"作成", r"新規", r"追加",
               r"생성", r"작성", r"추가",
               r"\bcrea[rd]?\b", r"\bcree\b", r"\ba[ñn]adir\b", r"\bagrega[r]?\b", r"\bcria[r]?\b", r"\badiciona[r]?\b",
               r"\berstelle[n]?\b", r"\banlegen\b", r"\bhinzuf[üu]gen\b", r"\bcr[ée]er\b", r"\bajouter\b",
               r"\bсоздать\b", r"\bсоздайте\b", r"\bдобавить\b", r"\bt[ạa]o\b", r"\bth[êe]m\b"],
    "modify": [r"修改", r"更新", r"调整", r"調整", r"重构", r"重構", r"修复", r"修復", r"改造", r"完善", r"扩展", r"擴展",
               r"优化", r"優化", r"替换", r"替換", r"注册", r"註冊", r"修正", r"変更", r"改修", r"編集", r"拡張", r"置換",
               r"수정", r"업데이트", r"변경", r"리팩터",
               r"\bactualiza[r]?\b", r"\bmodifica[r]?\b", r"\bedita[r]?\b", r"\bcambia[r]?\b", r"\bcorregir\b",
               r"\brefactoriza[r]?\b", r"\batualiza[r]?\b", r"\baltera[r]?\b", r"\bcorrigi[r]?\b",
               r"\baktualisieren\b", r"\b[äa]ndern\b", r"\banpassen\b", r"\bbearbeiten\b", r"\berweitern\b",
               r"\bmettre [àa] jour\b", r"\bmodifier\b", r"\bcorriger\b", r"\badapter\b",
               r"\bобновить\b", r"\bизменить\b", r"\bисправить\b", r"\bc[ậa]p nh[ậa]t\b", r"\bs[ửu]a\b", r"\bch[ỉi]nh\b"],
    "delete": [r"删除", r"刪除", r"移除", r"削除", r"삭제", r"제거",
               r"\belimina[r]?\b", r"\bborra[r]?\b", r"\bquita[r]?\b", r"\bremove[r]?\b", r"\bexclui[r]?\b",
               r"\bapaga[r]?\b", r"\bl[öo]schen\b", r"\bentfernen\b", r"\bsupprimer\b", r"\bretirer\b",
               r"\bудалить\b", r"\bx[óo]a\b"],
    "move": [r"移动", r"移動", r"重命名", r"迁移", r"遷移", r"迁到", r"改名", r"リネーム", r"名前を変更", r"이동", r"이름 변경",
             r"\bmove[r]?\b", r"\brenombra[r]?\b", r"\brenomea[r]?\b", r"\bverschieben\b", r"\bumbenennen\b",
             r"\bd[ée]placer\b", r"\brenommer\b", r"\bпереместить\b", r"\bпереименовать\b",
             r"\bdi chuy[ểe]n\b", r"\b[đd][ổo]i t[êe]n\b"],
}
OTHER_RE = [(intent, re.compile(p, re.IGNORECASE)) for intent, pats in OTHER.items() for p in pats]

INTO = re.compile(r"\b(?:to|in|into|inside|within|on)\b|中|里|裡|内|内に|に|에", re.IGNORECASE)
FROM = re.compile(r"\b(?:from|of|in|inside|within)\b|从|從|中|から|에서", re.IGNORECASE)
TOWARD = re.compile(r"\b(?:to|into|as)\b|→|->|=>|到|至|へ|に|으로|로", re.IGNORECASE)


def parse_checkbox(line):
    """(checked, text) for a checkbox line, else None."""
    m = CHECKBOX.match(line)
    return (m.group(1) in "xX", m.group(2)) if m else None


def strip_lead(text):
    """Drop numbers, markup and short 'LABEL:' prefixes from the start of a task."""
    prev = None
    while prev != text:
        prev = text
        text = LEAD.sub("", text, count=1)
    return text


def leading_word(text):
    m = re.match(r"([A-Za-z]+)", strip_lead(text))
    return m.group(1).lower() if m else ""


def path_position(text, code_path):
    """Where the path (or, failing that, its file name) appears in the text; -1 if absent."""
    pos = text.find(code_path)
    if pos < 0:
        pos = text.find(code_path.rsplit("/", 1)[-1])
    return pos


# "In `src/x.ts`, add ..." / "`src/x.ts`: update ..." / "`src/x.ts` — new file ..."
HEAD = re.compile(r"^(?P<in>(?:in|inside|within|for)\s+)?`?(?P<head>[^\s`:,—–]+)`?\s*(?:[:,—–]|\s-\s)\s*(?P<rest>.+)$",
                  re.IGNORECASE)


IN_CLAUSE = re.compile(r"^(?:in|inside|within)\s+(?P<clause>[^,:;]{1,240})[,:;]", re.IGNORECASE)
ZH_IN = re.compile(r"^在\s*(?P<clause>.{1,200}?)(?:中|的|里|裡|内|內)")


def in_file_clause(text, code_path):
    """'In `file` `fn()`, do X' / '在 `file` 中 ...': the task works inside an existing file."""
    t = strip_lead(text)
    m = IN_CLAUSE.match(t) or ZH_IN.match(t)
    if not m:
        return False
    clause = m["clause"]
    return code_path in clause or code_path.rsplit("/", 1)[-1] in clause


def classify_headed(text, code_path):
    """Lines that name a file first and then say what to do with it; None if not that shape."""
    m = HEAD.match(strip_lead(text))
    if not m or "/" not in m["head"] and "." not in m["head"]:
        return None
    head, rest = m["head"], m["rest"]
    if not (head == code_path or head.endswith(code_path.rsplit("/", 1)[-1])):
        return classify(rest, code_path)  # "In `src/`: create `a.ts`" -> judge a.ts by the rest
    intent, verb, role = classify(rest, "\0")  # path absent from the rest
    if intent == "other" and leading_word(rest) == "new":
        intent = "create"
    if m["in"] and intent in ("create", "delete", "move"):
        intent = "modify"  # "In `x.ts`, add/remove/move ..." changes x.ts
    elif intent == "create" and verb.lower() not in EN["create"].split()[:16]:
        intent = "modify"  # "`x.ts`: add ..." adds to x.ts
    elif intent in ("delete", "move") and leading_word(rest) not in {"delete", "deleted", "remove", "removed",
                                                                     "move", "moved", "rename", "renamed"}:
        intent = "modify"
    return intent, verb, role


def classify(text, code_path):
    """Return (intent, verb, move_role) for one task text and the path it names."""
    if not isinstance(text, str):
        return "other", "", ""
    if code_path != "\0":
        if in_file_clause(text, code_path):
            return "modify", "in", ""
        headed = classify_headed(text, code_path)
        if headed and headed[0] != "other":
            return headed
    pos = path_position(text, code_path)
    verb = leading_word(text)
    intent = EN_VERB.get(verb)
    verb_end = 0
    if intent:
        verb_end = text.lower().find(verb) + len(verb)
    else:
        hits = [(m.start(), m.end(), i, m.group(0)) for i, rx in OTHER_RE for m in [rx.search(text)] if m]
        if hits:
            start, verb_end, intent, verb = min(hits)
    if not intent:
        return "other", verb, ""

    between = text[verb_end:pos] if pos > verb_end else ""
    if intent == "create" and verb.lower() in {"add", "adds", "added", "添加", "增加", "新增", "追加", "추가",
                                               "añadir", "agregar", "adicionar", "hinzufügen", "ajouter",
                                               "добавить", "thêm"}:
        # "Add X to `file`" changes the file; "Add `file`" creates it.
        if pos >= 0 and INTO.search(between):
            intent = "modify"
        elif pos >= 0 and pos < verb_end - len(verb) and INTO.search(text[pos + len(code_path):verb_end]):
            intent = "modify"  # "在 `file` 中添加 ..." / "`file` に追加": file named before the verb
    if intent == "delete" and pos >= 0 and FROM.search(between):
        intent = "modify"  # "Remove X from `file`"
    role = ""
    if intent == "move":
        before = text[:pos] if pos >= 0 else ""
        role = "target" if TOWARD.search(before[verb_end:] if verb_end <= len(before) else before) else "source"
    return intent, verb, role
