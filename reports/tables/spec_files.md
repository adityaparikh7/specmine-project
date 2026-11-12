# `spec_files`

Broad-census spine: one row per spec file, full GitHub repository object, file/commit provenance, tool attribution, trace roll-ups. Raw Markdown is in specs.jsonl.gz.

- **Rows:** 470,795
- **Columns:** 124
- **Used for:** RQ2, RQ3: repository facts (stars, language, age) and which tool made each spec

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `file_url_sha16` | VARCHAR | 16-hex digest of the file's GitHub blob URL (primary key of the broad census). | 100% | 470,795 | 00001a8d79a8d283; 00001b3c90f61e5c; 00001d57c25efd70 |
| `file_url` | VARCHAR | GitHub blob URL of the spec file. | 100% | 470,795 | https://github.com/0-CYBERDYNE-SYSTEMS-0/FFT_nano/blob/891b128e4994ba3c98b1d0f56f2f07f9ce854b53/SPEC.md; https://github.com/0-CYBERDYNE-SYSTEMS-0/expert-prompting-eval/blob/894dedcd4841ab8190f342e4b6ea45f9e0caf0da/SPEC.md; https://github.com/0-CYBERDYNE-SYSTEMS-0/generative-cockpit/blob/547120e8426eaa12ca2930d8cdf4ddc9fc2a9cab/SPEC.md |
| `file_path` | VARCHAR | path within its repository. | 100% | 386,054 | spec.md; SPEC.md; src/spec.md |
| `file_name` | VARCHAR | file name. | 100% | 13 | spec.md; SPEC.md; specs.md |
| `file_sha` | VARCHAR |  | 100% | 416,712 | cb0872ca7e8449ade5c9129b5de7abda346bd415; c67d9149807eadb0891e4d57b511ba325e7087d1; a464c0b385115686117c8981067157d02f1cb958 |
| `git_url` | VARCHAR |  | 100% | 430,867 | https://api.github.com/repositories/1060758327/git/blobs/cb0872ca7e8449ade5c9129b5de7abda346bd415; https://api.github.com/repositories/984900169/git/blobs/7c48421adbcbc7177d8df220db69eff89aee140c; https://api.github.com/repositories/984900169/git/blobs/3c549f084cc2cf17e05027a23fab17fb5945ece8 |
| `search_run_id` | VARCHAR |  | 100% | 1 | spec_2024_2026 |
| `repo_id` | BIGINT |  | 100% | 73,011 | 1152827966; 1189219232; 984900169 |
| `repo_node_id` | VARCHAR |  | 100% | 73,011 | R_kgDORLbCPg; R_kgDORuILoA; R_kgDOOrRiSQ |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 73,031 | langoai/lango; BlackBeltTechnology/pi-agent-dashboard; docxology/codomyrmex |
| `repo_url` | VARCHAR |  | 100% | 73,031 | https://github.com/langoai/lango; https://github.com/BlackBeltTechnology/pi-agent-dashboard; https://github.com/docxology/codomyrmex |
| `repo_homepage` | VARCHAR |  | 37% | 10,420 | ; https://langoai.github.io/lango; https://docxology.github.io/codomyrmex/ |
| `repo_description` | VARCHAR |  | 60% | 43,743 | A high-performance AI agent built with Go; Real-time web dashboard for pi coding-agent sessions. Multi-session view, live chat mirroring, integrated terminal, diff …; 🐜 AI-native modular coding workspace — 127 modules, 424 MCP tools, 21K+ zero-mock tests, multi-agent orchestration (Clau … |
| `repo_fork` | BIGINT |  | 100% | 1 | 0 |
| `repo_private` | BIGINT |  | 100% | 1 | 0 |
| `repo_visibility` | VARCHAR |  | 100% | 1 | public |
| `owner_login` | VARCHAR | repository owner's GitHub login. | 100% | 44,521 | caffeinepub; langoai; BlackBeltTechnology |
| `owner_id` | BIGINT |  | 100% | 44,519 | 249769834; 263160785; 8101592 |
| `owner_node_id` | VARCHAR |  | 100% | 44,519 | O_kgDODuMvag; O_kgDOD6-D0Q; MDEyOk9yZ2FuaXphdGlvbjgxMDE1OTI= |
| `owner_type` | VARCHAR | User or Organization. | 100% | 2 | User; Organization |
| `owner_html_url` | VARCHAR |  | 100% | 44,521 | https://github.com/caffeinepub; https://github.com/langoai; https://github.com/BlackBeltTechnology |
| `owner_site_admin` | BIGINT |  | 100% | 2 | 0; 1 |
| `repo_stars` | BIGINT | star count at capture time. | 100% | 720 | 0; 1; 2 |
| `repo_forks` | BIGINT |  | 100% | 349 | 0; 1; 2 |
| `repo_watchers` | BIGINT |  | 100% | 720 | 0; 1; 2 |
| `repo_subscribers_count` | BIGINT |  | 100% | 146 | 0; 1; 2 |
| `repo_network_count` | BIGINT |  | 100% | 349 | 0; 1; 2 |
| `repo_open_issues` | BIGINT |  | 100% | 335 | 0; 1; 2 |
| `repo_size_kb` | BIGINT |  | 100% | 22,374 | 17802; 61685; 87783 |
| `repo_language` | VARCHAR | primary language. | 99% | 198 | TypeScript; Python; Rust |
| `repo_license` | VARCHAR |  | 48% | 34 | MIT License; Apache License 2.0; Other |
| `repo_license_key` | VARCHAR |  | 48% | 34 | mit; apache-2.0; other |
| `repo_license_spdx_id` | VARCHAR | SPDX id of the repo license (NULL/NOASSERTION if none). | 48% | 34 | MIT; Apache-2.0; NOASSERTION |
| `repo_default_branch` | VARCHAR |  | 100% | 1,715 | main; master; develop |
| `repo_topics` | VARCHAR |  | 100% | 7,193 | ; adk-go, ai-agents, claude-code, go, graphrag, openclaw-alternative, openspec, rag, security, self-learning, sqlite-vec; agents, ai, ai-agents, claude, developer-tools, llm, mcp, model-context-protocol, modular, multi-agent, orchestration, p … |
| `repo_archived` | BIGINT |  | 100% | 2 | 0; 1 |
| `repo_disabled` | BIGINT |  | 100% | 1 | 0 |
| `repo_is_template` | BIGINT |  | 100% | 2 | 0; 1 |
| `repo_allow_forking` | BIGINT |  | 100% | 1 | 1 |
| `repo_web_commit_signoff_required` | BIGINT |  | 100% | 2 | 0; 1 |
| `repo_has_issues` | BIGINT |  | 100% | 2 | 1; 0 |
| `repo_has_projects` | BIGINT |  | 100% | 2 | 1; 0 |
| `repo_has_wiki` | BIGINT |  | 100% | 2 | 1; 0 |
| `repo_has_pages` | BIGINT |  | 100% | 2 | 0; 1 |
| `repo_has_downloads` | BIGINT |  | 100% | 2 | 1; 0 |
| `repo_has_discussions` | BIGINT |  | 100% | 2 | 0; 1 |
| `repo_clone_url` | VARCHAR |  | 100% | 73,031 | https://github.com/langoai/lango.git; https://github.com/BlackBeltTechnology/pi-agent-dashboard.git; https://github.com/docxology/codomyrmex.git |
| `repo_ssh_url` | VARCHAR |  | 100% | 73,031 | git@github.com:langoai/lango.git; git@github.com:BlackBeltTechnology/pi-agent-dashboard.git; git@github.com:docxology/codomyrmex.git |
| `repo_svn_url` | VARCHAR |  | 100% | 73,031 | https://github.com/langoai/lango; https://github.com/BlackBeltTechnology/pi-agent-dashboard; https://github.com/docxology/codomyrmex |
| `repo_git_url` | VARCHAR |  | 100% | 73,031 | git://github.com/langoai/lango.git; git://github.com/BlackBeltTechnology/pi-agent-dashboard.git; git://github.com/docxology/codomyrmex.git |
| `repo_mirror_url` | VARCHAR |  | 0% | 0 |  |
| `repo_created_at` | VARCHAR |  | 100% | 72,757 | 2026-02-08T13:57:06Z; 2026-03-23T05:08:48Z; 2025-05-16T17:45:28Z |
| `repo_updated_at` | VARCHAR |  | 100% | 72,679 | 2026-05-26T16:13:10Z; 2026-07-06T22:21:07Z; 2026-07-03T19:18:51Z |
| `repo_pushed_at` | VARCHAR |  | 100% | 72,758 | 2026-06-18T22:58:42Z; 2026-07-06T22:21:02Z; 2026-07-07T01:56:04Z |
| `file_last_commit_sha` | VARCHAR |  | 100% | 190,988 | d8b5f593166517ab81528e525cc960432522bfe1; 0c0aa68b95748b7120b4c71e3fe3a8bcef67fa4d; ffb46f258ff833f0d8a674314d55cd229ab4d7b6 |
| `file_last_commit_node_id` | VARCHAR |  | 100% | 192,694 | C_kwDOQOR5qNoAKGQ4YjVmNTkzMTY2NTE3YWI4MTUyOGU1MjVjYzk2MDQzMjUyMmJmZTE; C_kwDOOZP2QdoAKDBjMGFhNjhiOTU3NDhiNzEyMGI0YzcxZTNmZTNhOGJjZWY2N2ZhNGQ; C_kwDORLbCPtoAKGZmYjQ2ZjI1OGZmODMzZjBkOGE2NzQzMTRkNTVjZDIyOWFiNGQ3YjY |
| `file_last_commit_html_url` | VARCHAR |  | 100% | 192,785 | https://github.com/gesad-lab/baes_berk_20251103/commit/d8b5f593166517ab81528e525cc960432522bfe1; https://github.com/metorial/metorial/commit/0c0aa68b95748b7120b4c71e3fe3a8bcef67fa4d; https://github.com/langoai/lango/commit/ffb46f258ff833f0d8a674314d55cd229ab4d7b6 |
| `file_last_commit_message` | VARCHAR |  | 100% | ~187,124 | Initial commit |
| `file_last_commit_comment_count` | BIGINT |  | 100% | 4 | 0; 1; 3 |
| `file_last_commit_at` | VARCHAR | timestamp of the most recent commit to the file. | 100% | 189,489 | 2025-11-03T11:48:53Z; 2026-07-02T07:36:38Z; 2026-05-16T23:33:20Z |
| `file_last_commit_author` | VARCHAR |  | 100% | 57,545 | langowarny; Claude; Tobias Herber |
| `file_last_commit_author_login` | VARCHAR |  | 87% | 39,331 | langowarny; claude; docxology |
| `file_last_commit_author_id` | BIGINT |  | 87% | 39,329 | 203519390; 81847; 6911384 |
| `file_last_commit_author_type` | VARCHAR |  | 87% | 3 | User; Bot; Organization |
| `file_last_commit_author_html_url` | VARCHAR |  | 87% | 39,332 | https://github.com/langowarny; https://github.com/claude; https://github.com/docxology |
| `file_last_commit_author_site_admin` | BIGINT |  | 87% | 2 | 0; 1 |
| `file_last_commit_committer` | VARCHAR |  | 100% | 53,573 | GitHub; langowarny; Claude |
| `file_last_commit_committer_at` | VARCHAR |  | 100% | 188,449 | 2025-11-03T11:48:53Z; 2026-07-02T07:36:38Z; 2026-05-16T23:33:20Z |
| `file_last_commit_committer_login` | VARCHAR |  | 87% | 35,861 | web-flow; langowarny; claude |
| `file_last_commit_committer_id` | BIGINT |  | 87% | 35,859 | 19864447; 203519390; 81847 |
| `file_last_commit_committer_type` | VARCHAR |  | 87% | 3 | User; Bot; Organization |
| `file_last_commit_committer_html_url` | VARCHAR |  | 87% | 35,862 | https://github.com/web-flow; https://github.com/langowarny; https://github.com/claude |
| `file_last_commit_committer_site_admin` | BIGINT |  | 87% | 2 | 0; 1 |
| `file_last_commit_tree_sha` | VARCHAR |  | 100% | 190,845 | 7ec0ac9e529664d0d3692bb0ac1601242b5c7ef0; 48e04fe910d29b09d4ec140254c46f3c9d356ee1; 10ccaa082b0c605e3bb046261ad80f7605d8b748 |
| `file_last_commit_parents` | VARCHAR |  | 92% | 177,317 | c4c38f74f75a577e4458b4fe38827aa8a13eaad7; 89815845adc839ba64cdcc1a38e8311108a306c7; 322ddf97f3f6500ea28205b52f091cef29d1b728 |
| `file_last_commit_verified` | BIGINT |  | 100% | 2 | 0; 1 |
| `file_last_commit_verification_reason` | VARCHAR |  | 100% | 9 | unsigned; valid; unknown_key |
| `file_last_commit_verified_at` | VARCHAR |  | 18% | 32,602 | 2026-03-09T01:40:23Z; 2026-06-21T18:22:13Z; 2026-04-10T22:40:40Z |
| `size_partition_label` | VARCHAR |  | 100% | 3,736 | size_3139_to_3141; size_2242_to_2245; size_2247_to_2250 |
| `updated_at` | VARCHAR |  | 100% | 25 | 2026-07-22 09:34:57; 2026-07-22 09:35:28; 2026-07-22 09:35:52 |
| `not_spec_filter` | BIGINT | 0 for kept specs (only kept rows ship). | 100% | 1 | 0 |
| `file_first_commit_sha` | VARCHAR |  | 100% | 190,770 | d8b5f593166517ab81528e525cc960432522bfe1; 0c0aa68b95748b7120b4c71e3fe3a8bcef67fa4d; d0368668d4df1f9126102d0a0b275b0460ea189b |
| `file_first_commit_node_id` | VARCHAR |  | 100% | 192,738 | C_kwDOQOR5qNoAKGQ4YjVmNTkzMTY2NTE3YWI4MTUyOGU1MjVjYzk2MDQzMjUyMmJmZTE; C_kwDOOZP2QdoAKDBjMGFhNjhiOTU3NDhiNzEyMGI0YzcxZTNmZTNhOGJjZWY2N2ZhNGQ; C_kwDOSBRG4NoAKGQwMzY4NjY4ZDRkZjFmOTEyNjEwMmQwYTBiMjc1YjA0NjBlYTE4OWI |
| `file_first_commit_html_url` | VARCHAR |  | 100% | 192,740 | https://github.com/gesad-lab/baes_berk_20251103/commit/d8b5f593166517ab81528e525cc960432522bfe1; https://github.com/metorial/metorial/commit/0c0aa68b95748b7120b4c71e3fe3a8bcef67fa4d; https://github.com/metorial/integrations/commit/d0368668d4df1f9126102d0a0b275b0460ea189b |
| `file_first_commit_message` | VARCHAR |  | 100% | ~173,700 | Initial commit |
| `file_first_commit_comment_count` | BIGINT |  | 100% | 4 | 0; 1; 3 |
| `file_first_commit_at` | VARCHAR | timestamp the file was first committed (adoption signal). | 100% | 188,975 | 2025-11-03T11:48:53Z; 2026-07-02T07:36:38Z; 2026-04-13T09:45:51Z |
| `file_first_commit_author` | VARCHAR |  | 100% | 57,263 | langowarny; Claude; Tobias Herber |
| `file_first_commit_author_login` | VARCHAR |  | 87% | 38,858 | langowarny; claude; docxology |
| `file_first_commit_author_id` | BIGINT |  | 87% | 38,859 | 203519390; 81847; 6911384 |
| `file_first_commit_author_type` | VARCHAR |  | 87% | 3 | User; Bot; Organization |
| `file_first_commit_author_html_url` | VARCHAR |  | 87% | 38,859 | https://github.com/langowarny; https://github.com/claude; https://github.com/docxology |
| `file_first_commit_author_site_admin` | BIGINT |  | 87% | 2 | 0; 1 |
| `file_first_commit_committer` | VARCHAR |  | 100% | 53,920 | GitHub; langowarny; Claude |
| `file_first_commit_committer_at` | VARCHAR |  | 100% | 187,951 | 2025-11-03T11:48:53Z; 2026-07-02T07:36:38Z; 2026-04-13T09:45:51Z |
| `file_first_commit_committer_login` | VARCHAR |  | 87% | 36,016 | web-flow; langowarny; claude |
| `file_first_commit_committer_id` | BIGINT |  | 87% | 36,017 | 19864447; 203519390; 81847 |
| `file_first_commit_committer_type` | VARCHAR |  | 87% | 3 | User; Bot; Organization |
| `file_first_commit_committer_html_url` | VARCHAR |  | 87% | 36,017 | https://github.com/web-flow; https://github.com/langowarny; https://github.com/claude |
| `file_first_commit_committer_site_admin` | BIGINT |  | 87% | 2 | 0; 1 |
| `file_first_commit_tree_sha` | VARCHAR |  | 100% | 190,568 | 7ec0ac9e529664d0d3692bb0ac1601242b5c7ef0; 48e04fe910d29b09d4ec140254c46f3c9d356ee1; 03b6465d89dfe76ee394af47bd8bc78f041a67c8 |
| `file_first_commit_parents` | VARCHAR |  | 90% | 171,095 | c4c38f74f75a577e4458b4fe38827aa8a13eaad7; 9cd61155576729551dc544b9bcd3d07f0dd60fa6; 89815845adc839ba64cdcc1a38e8311108a306c7 |
| `file_first_commit_verified` | BIGINT |  | 100% | 2 | 0; 1 |
| `file_first_commit_verification_reason` | VARCHAR |  | 100% | 9 | unsigned; valid; unknown_key |
| `file_first_commit_verified_at` | VARCHAR |  | 18% | 31,760 | 2026-03-09T01:40:23Z; 2026-06-21T18:22:13Z; 2026-07-04T17:51:53Z |
| `file_total_commits` | BIGINT | How many commits changed this file. | 100% | 158 | 1; 2; 3 |
| `commit_history_status` | VARCHAR |  | 100% | 2 | done; empty |
| `commit_history_fetched_at` | VARCHAR |  | 100% | 16,023 | 2026-07-11T03:42:54Z; 2026-07-11T01:26:22Z; 2026-07-11T01:35:45Z |
| `spec_tool` | VARCHAR | Which spec-driven tool made the file (openspec, speckit, kiro, ...), guessed from its path. | 100% | 21 | openspec; speckit; adhoc_other |
| `spec_role` | VARCHAR | OpenSpec: living = current spec, change_proposal = change in progress, archived = finished change. | 100% | 6 | archived; na; living |
| `file_content_sha` | VARCHAR |  | 99% | 414,767 | f38a904f0307b75d125b5e679633eabb5eaf90fd946d3a5e0897d2bbb51c4f2c; bd529dda1cccaaee34fce4355100c5bfcf56d3811698c6aa7dbab5f6b5476c60; 332d3f5bb0f7c3995f05a0d5f22c3964da43c06d647b6a39c6c454927ec7a820 |
| `file_content_bytes` | BIGINT |  | 99% | 35,746 | 3960; 3140; 50998 |
| `content_fetch_status` | VARCHAR |  | 100% | 2 | done; missing |
| `content_fetched_at` | VARCHAR |  | 100% | 200 | 2026-07-12T01:11:46Z; 2026-07-12T01:11:59Z; 2026-07-12T01:12:11Z |
| `feature_branch` | VARCHAR | the 'Feature Branch:' header value, when present. | 9% | 37,838 | es; checked; main |
| `n_linked_prs` | BIGINT | rolled-up PR references. | 100% | 75 | 0; 1; 2 |
| `n_linked_issues` | BIGINT | rolled-up issue references. | 100% | 27 | 0; 1; 2 |
| `n_sibling_docs` | BIGINT | rolled-up sibling-document references. | 100% | 77 | 3; 0; 2 |
| `n_code_links` | BIGINT | rolled-up code-file references. | 100% | 72 | 0; 1; 2 |
| `has_tasks` | BIGINT | has an associated tasks.md. | 100% | 2 | 1; 0 |
| `has_plan` | BIGINT | has a plan.md. | 100% | 2 | 0; 1 |
| `has_proposal` | BIGINT | has a proposal.md. | 100% | 2 | 0; 1 |
| `has_design` | BIGINT | has a design.md. | 100% | 2 | 0; 1 |
| `trace_rollup_at` | VARCHAR |  | 100% | 1 | 2026-07-21T17:18:38Z |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `file_url_sha16` | 04753740a4f7974d | 050a019bb902ee4f | 0672cbd1a323050b |
| `file_url` | https://github.com/foxzool/openlark/blob/f064677377c99656abc3f9e1af2959b6d32c79ea/openspec/changes/archive/2026-06-30-un … | https://github.com/CETANGZHI/flowainew/blob/94cc7095db1259c5f1cb053bdf5c74bb0c4c16c3/specs/013-profile-style-alignment-a … | https://github.com/ContextLab/llmXive/blob/ff5ed4b2b85a37efc3aa468ec39a9532af80775f/projects/PROJ-723-resting-state-fmri … |
| `file_path` | openspec/changes/archive/2026-06-30-unify-platform-admin-request-naming/specs/platform-admin-request-naming/spec.md | specs/013-profile-style-alignment-and-drift-detection/spec.md | projects/PROJ-723-resting-state-fmri-global-signal-as-a-ma/specs/001-resting-state-fmri-global-signal-as-a-ma/spec.md |
| `file_name` | spec.md | spec.md | spec.md |
| `file_sha` | ac5c2a179402769a96ec5f1c05977ac36ff75abc | 94f41dc6d0aaa5972faa54d9606e94429270f3b0 | 7b2fd47cb305ebc4c10758277c213e8e456b93d6 |
| `git_url` | https://api.github.com/repositories/784210473/git/blobs/ac5c2a179402769a96ec5f1c05977ac36ff75abc | https://api.github.com/repositories/1098261080/git/blobs/94f41dc6d0aaa5972faa54d9606e94429270f3b0 | https://api.github.com/repositories/1013289646/git/blobs/7b2fd47cb305ebc4c10758277c213e8e456b93d6 |
| `search_run_id` | spec_2024_2026 | spec_2024_2026 | spec_2024_2026 |
| `repo_id` | 784210473 | 1098261080 | 1013289646 |
| `repo_node_id` | R_kgDOLr4aKQ | R_kgDOQXYiWA | R_kgDOPGWSrg |
| `repo_name` | foxzool/openlark | CETANGZHI/flowainew | ContextLab/llmXive |
| `repo_url` | https://github.com/foxzool/openlark | https://github.com/CETANGZHI/flowainew | https://github.com/ContextLab/llmXive |
| `repo_homepage` |  | (empty) | https://contextlab.github.io/llmXive/ |
| `repo_description` | 飞书开放平台的非官方 Rust SDK，支持自定义机器人、长连接机器人、云文档、飞书卡片、消息、群组等 API 调用。 | flowainew | llmXive is an LLM-driven system for automating scientific discovery |
| `repo_fork` | 0 | 0 | 0 |
| `repo_private` | 0 | 0 | 0 |
| `repo_visibility` | public | public | public |
| `owner_login` | foxzool | CETANGZHI | ContextLab |
| `owner_id` | 217027 | 225927178 | 22374976 |
| `owner_node_id` | MDQ6VXNlcjIxNzAyNw== | U_kgDODXdgCg | MDEyOk9yZ2FuaXphdGlvbjIyMzc0OTc2 |
| `owner_type` | User | User | Organization |
| `owner_html_url` | https://github.com/foxzool | https://github.com/CETANGZHI | https://github.com/ContextLab |
| `owner_site_admin` | 0 | 0 | 0 |
| `repo_stars` | 98 | 1 | 2 |
| `repo_forks` | 26 | 0 | 2 |
| `repo_watchers` | 98 | 1 | 2 |
| `repo_subscribers_count` | 1 | 0 | 0 |
| `repo_network_count` | 26 | 0 | 2 |
| `repo_open_issues` | 5 | 1 | 15 |
| `repo_size_kb` | 25687 | 80251 | 7402511 |
| `repo_language` | Rust | Python | TeX |
| `repo_license` | Apache License 2.0 | (empty) | MIT License |
| `repo_license_key` | apache-2.0 | (empty) | mit |
| `repo_license_spdx_id` | Apache-2.0 | (empty) | MIT |
| `repo_default_branch` | main | main | main |
| `repo_topics` | feishu, feishu-bot, feishu-sdk, lark, lark-bot, lark-sdk, rust |  | autonomous-systems, llm, robot-scientist |
| `repo_archived` | 0 | 0 | 0 |
| `repo_disabled` | 0 | 0 | 0 |
| `repo_is_template` | 0 | 0 | 0 |
| `repo_allow_forking` | 1 | 1 | 1 |
| `repo_web_commit_signoff_required` | 0 | 0 | 0 |
| `repo_has_issues` | 1 | 1 | 1 |
| `repo_has_projects` | 1 | 1 | 1 |
| `repo_has_wiki` | 1 | 0 | 1 |
| `repo_has_pages` | 1 | 0 | 1 |
| `repo_has_downloads` | 1 | 1 | 1 |
| `repo_has_discussions` | 0 | 0 | 1 |
| `repo_clone_url` | https://github.com/foxzool/openlark.git | https://github.com/CETANGZHI/flowainew.git | https://github.com/ContextLab/llmXive.git |
| `repo_ssh_url` | git@github.com:foxzool/openlark.git | git@github.com:CETANGZHI/flowainew.git | git@github.com:ContextLab/llmXive.git |
| `repo_svn_url` | https://github.com/foxzool/openlark | https://github.com/CETANGZHI/flowainew | https://github.com/ContextLab/llmXive |
| `repo_git_url` | git://github.com/foxzool/openlark.git | git://github.com/CETANGZHI/flowainew.git | git://github.com/ContextLab/llmXive.git |
| `repo_mirror_url` | (empty) | (empty) | (empty) |
| `repo_created_at` | 2024-04-09T12:05:55Z | 2025-11-17T13:17:09Z | 2025-07-03T16:47:31Z |
| `repo_updated_at` | 2026-07-07T02:49:20Z | 2026-03-17T03:51:51Z | 2026-07-07T02:07:04Z |
| `repo_pushed_at` | 2026-07-07T02:49:17Z | 2026-01-14T11:46:46Z | 2026-07-07T02:07:00Z |
| `file_last_commit_sha` | 0f1e5e3b52c960502767232eb0a5a556759a069b | 2021fb709db442903f2941bdbd2a353a38d4e876 | 110d62980833962754e17b9f138425a227ab2031 |
| `file_last_commit_node_id` | C_kwDOLr4aKdoAKDBmMWU1ZTNiNTJjOTYwNTAyNzY3MjMyZWIwYTVhNTU2NzU5YTA2OWI | C_kwDOQXYiWNoAKDIwMjFmYjcwOWRiNDQyOTAzZjI5NDFiZGJkMmEzNTNhMzhkNGU4NzY | C_kwDOPGWSrtoAKDExMGQ2Mjk4MDgzMzk2Mjc1NGUxN2I5ZjEzODQyNWEyMjdhYjIwMzE |
| `file_last_commit_html_url` | https://github.com/foxzool/openlark/commit/0f1e5e3b52c960502767232eb0a5a556759a069b | https://github.com/CETANGZHI/flowainew/commit/2021fb709db442903f2941bdbd2a353a38d4e876 | https://github.com/ContextLab/llmXive/commit/110d62980833962754e17b9f138425a227ab2031 |
| `file_last_commit_message` | chore(openspec): 归档 change unify-platform-admin-request-naming（platform admin 批） ⏎  ⏎ delta spec platform-admin-request- … | Upload project files to GitHub | advance(worker 4): tick |
| `file_last_commit_comment_count` | 0 | 0 | 0 |
| `file_last_commit_at` | 2026-06-30T04:23:11Z | 2025-12-23T02:42:22Z | 2026-07-03T19:25:24Z |
| `file_last_commit_author` | ZoOL | CETANGZHI | github-actions[bot] |
| `file_last_commit_author_login` | foxzool | CETANGZHI | github-actions[bot] |
| `file_last_commit_author_id` | 217027 | 225927178 | 41898282 |
| `file_last_commit_author_type` | User | User | Bot |
| `file_last_commit_author_html_url` | https://github.com/foxzool | https://github.com/CETANGZHI | https://github.com/apps/github-actions |
| `file_last_commit_author_site_admin` | 0 | 0 | 0 |
| `file_last_commit_committer` | ZoOL | CETANGZHI | github-actions[bot] |
| `file_last_commit_committer_at` | 2026-06-30T04:23:11Z | 2025-12-23T02:42:22Z | 2026-07-03T19:25:38Z |
| `file_last_commit_committer_login` | foxzool | CETANGZHI | github-actions[bot] |
| `file_last_commit_committer_id` | 217027 | 225927178 | 41898282 |
| `file_last_commit_committer_type` | User | User | Bot |
| `file_last_commit_committer_html_url` | https://github.com/foxzool | https://github.com/CETANGZHI | https://github.com/apps/github-actions |
| `file_last_commit_committer_site_admin` | 0 | 0 | 0 |
| `file_last_commit_tree_sha` | 6559ef40c1b0ee081e656d37102199b15a32397c | 32f0dccfd9aa395dd7d8f621d3a04d148aca6cdc | 8c09ec699585d98999af72a4396816d4e9773340 |
| `file_last_commit_parents` | e52cc2b85bb05165935f6d3f6800064c8255d3dd | a1c9218f087fbee8999c559974da3f1ed3078c5a | ab8a6ea646089a4418fe1da417cbb518eeaeadfa |
| `file_last_commit_verified` | 1 | 0 | 0 |
| `file_last_commit_verification_reason` | valid | unsigned | unsigned |
| `file_last_commit_verified_at` | 2026-06-30T04:23:14Z | (empty) | (empty) |
| `size_partition_label` | size_1247_to_1248 | size_3619_to_3622 | size_11581_to_11601 |
| `updated_at` | 2026-07-22 09:34:57 | 2026-07-22 09:35:52 | 2026-07-22 09:35:52 |
| `not_spec_filter` | 0 | 0 | 0 |
| `file_first_commit_sha` | 0f1e5e3b52c960502767232eb0a5a556759a069b | 2021fb709db442903f2941bdbd2a353a38d4e876 | 110d62980833962754e17b9f138425a227ab2031 |
| `file_first_commit_node_id` | C_kwDOLr4aKdoAKDBmMWU1ZTNiNTJjOTYwNTAyNzY3MjMyZWIwYTVhNTU2NzU5YTA2OWI | C_kwDOQXYiWNoAKDIwMjFmYjcwOWRiNDQyOTAzZjI5NDFiZGJkMmEzNTNhMzhkNGU4NzY | C_kwDOPGWSrtoAKDExMGQ2Mjk4MDgzMzk2Mjc1NGUxN2I5ZjEzODQyNWEyMjdhYjIwMzE |
| `file_first_commit_html_url` | https://github.com/foxzool/openlark/commit/0f1e5e3b52c960502767232eb0a5a556759a069b | https://github.com/CETANGZHI/flowainew/commit/2021fb709db442903f2941bdbd2a353a38d4e876 | https://github.com/ContextLab/llmXive/commit/110d62980833962754e17b9f138425a227ab2031 |
| `file_first_commit_message` | chore(openspec): 归档 change unify-platform-admin-request-naming（platform admin 批） ⏎  ⏎ delta spec platform-admin-request- … | Upload project files to GitHub | advance(worker 4): tick |
| `file_first_commit_comment_count` | 0 | 0 | 0 |
| `file_first_commit_at` | 2026-06-30T04:23:11Z | 2025-12-23T02:42:22Z | 2026-07-03T19:25:24Z |
| `file_first_commit_author` | ZoOL | CETANGZHI | github-actions[bot] |
| `file_first_commit_author_login` | foxzool | CETANGZHI | github-actions[bot] |
| `file_first_commit_author_id` | 217027 | 225927178 | 41898282 |
| `file_first_commit_author_type` | User | User | Bot |
| `file_first_commit_author_html_url` | https://github.com/foxzool | https://github.com/CETANGZHI | https://github.com/apps/github-actions |
| `file_first_commit_author_site_admin` | 0 | 0 | 0 |
| `file_first_commit_committer` | ZoOL | CETANGZHI | github-actions[bot] |
| `file_first_commit_committer_at` | 2026-06-30T04:23:11Z | 2025-12-23T02:42:22Z | 2026-07-03T19:25:38Z |
| `file_first_commit_committer_login` | foxzool | CETANGZHI | github-actions[bot] |
| `file_first_commit_committer_id` | 217027 | 225927178 | 41898282 |
| `file_first_commit_committer_type` | User | User | Bot |
| `file_first_commit_committer_html_url` | https://github.com/foxzool | https://github.com/CETANGZHI | https://github.com/apps/github-actions |
| `file_first_commit_committer_site_admin` | 0 | 0 | 0 |
| `file_first_commit_tree_sha` | 6559ef40c1b0ee081e656d37102199b15a32397c | 32f0dccfd9aa395dd7d8f621d3a04d148aca6cdc | 8c09ec699585d98999af72a4396816d4e9773340 |
| `file_first_commit_parents` | e52cc2b85bb05165935f6d3f6800064c8255d3dd | a1c9218f087fbee8999c559974da3f1ed3078c5a | ab8a6ea646089a4418fe1da417cbb518eeaeadfa |
| `file_first_commit_verified` | 1 | 0 | 0 |
| `file_first_commit_verification_reason` | valid | unsigned | unsigned |
| `file_first_commit_verified_at` | 2026-06-30T04:23:14Z | (empty) | (empty) |
| `file_total_commits` | 1 | 1 | 1 |
| `commit_history_status` | done | done | done |
| `commit_history_fetched_at` | 2026-07-11T00:58:45Z | 2026-07-11T00:59:22Z | 2026-07-11T01:00:50Z |
| `spec_tool` | openspec | speckit | speckit |
| `spec_role` | archived | feature | feature |
| `file_content_sha` | f8f06094fa239be5e15af67b0e2beab1a409f091389b1a08416bfe19035c4175 | 29fcd871d340a615955c728f3e8794c6f7b11ff9d18f3f06fa0dc222b5ea1e65 | 7f5384f60d4ee0b4036286e226353f5795df21e5b9866a956d3bbcdb351d0ec5 |
| `file_content_bytes` | 1247 | 3622 | 11599 |
| `content_fetch_status` | done | done | done |
| `content_fetched_at` | 2026-07-12T01:12:11Z | 2026-07-12T01:12:11Z | 2026-07-12T01:12:23Z |
| `feature_branch` | (empty) | (empty) | 001-gene-regulation |
| `n_linked_prs` | 0 | 0 | 0 |
| `n_linked_issues` | 0 | 0 | 0 |
| `n_sibling_docs` | 3 | 1 | 0 |
| `n_code_links` | 0 | 0 | 0 |
| `has_tasks` | 1 | 1 | 0 |
| `has_plan` | 0 | 0 | 0 |
| `has_proposal` | 1 | 0 | 0 |
| `has_design` | 1 | 0 | 0 |
| `trace_rollup_at` | 2026-07-21T17:18:38Z | 2026-07-21T17:18:38Z | 2026-07-21T17:18:38Z |
