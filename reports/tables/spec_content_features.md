# `spec_content_features`

39 parsed structural and requirement-template features per spec.

- **Rows:** 468,307
- **Columns:** 40
- **Used for:** Not used

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `file_url_sha16` | VARCHAR | 16-hex digest of the file's GitHub blob URL (primary key of the broad census). | 100% | 468,307 | 00001a8d79a8d283; 00001b3c90f61e5c; 00001d57c25efd70 |
| `n_bytes` | BIGINT |  | 100% | 35,746 | 3960; 3140; 50998 |
| `n_lines` | BIGINT |  | 100% | 2,538 | 31; 35; 30 |
| `n_words` | BIGINT |  | 100% | 8,842 | 82; 188; 187 |
| `n_headings` | BIGINT |  | 100% | 339 | 7; 5; 6 |
| `max_heading_depth` | BIGINT |  | 100% | 7 | 4; 3; 2 |
| `n_code_fences` | BIGINT |  | 100% | 188 | 0; 1; 2 |
| `n_mermaid` | BIGINT |  | 100% | 32 | 0; 1; 2 |
| `n_tables` | BIGINT |  | 100% | 108 | 0; 1; 2 |
| `n_links` | BIGINT |  | 100% | 184 | 0; 1; 2 |
| `n_images` | BIGINT |  | 100% | 35 | 0; 1; 2 |
| `n_list_items` | BIGINT |  | 100% | 950 | 12; 8; 6 |
| `n_checkboxes` | BIGINT |  | 100% | 207 | 0; 5; 6 |
| `n_checked` | BIGINT |  | 100% | 134 | 0; 16; 1 |
| `n_shall` | BIGINT |  | 100% | 367 | 0; 3; 2 |
| `n_gherkin` | BIGINT |  | 100% | 425 | 0; 6; 12 |
| `n_scenario_blocks` | BIGINT |  | 100% | 227 | 0; 3; 4 |
| `n_delta_headers` | BIGINT |  | 100% | 20 | 0; 1; 2 |
| `n_needs_clarification` | BIGINT |  | 100% | 31 | 0; 1; 2 |
| `n_todo` | BIGINT |  | 100% | 55 | 0; 1; 2 |
| `has_ears` | BIGINT |  | 100% | 2 | 1; 0 |
| `has_gherkin` | BIGINT |  | 100% | 2 | 1; 0 |
| `has_user_story` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_requirements` | BIGINT |  | 100% | 2 | 1; 0 |
| `has_acceptance_criteria` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_user_scenarios` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_non_goals` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_out_of_scope` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_overview` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_success_criteria` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_edge_cases` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_open_questions` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_dependencies` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_purpose` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_mandatory_marker` | BIGINT |  | 100% | 2 | 0; 1 |
| `is_tiny` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_unfilled_placeholder` | BIGINT |  | 100% | 2 | 0; 1 |
| `has_lorem` | BIGINT |  | 100% | 2 | 0; 1 |
| `lang` | VARCHAR |  | 100% | 44 | en; es; pt |
| `content_family` | VARCHAR |  | 100% | 6 | openspec; unknown; speckit |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `file_url_sha16` | 047b52bc5c65878f | 050e9043a792ef1c | 067adf28fa9006a5 |
| `n_bytes` | 2193 | 4970 | 2793 |
| `n_lines` | 45 | 100 | 69 |
| `n_words` | 161 | 606 | 409 |
| `n_headings` | 10 | 14 | 14 |
| `max_heading_depth` | 4 | 4 | 4 |
| `n_code_fences` | 0 | 1 | 0 |
| `n_mermaid` | 0 | 0 | 0 |
| `n_tables` | 0 | 0 | 0 |
| `n_links` | 0 | 0 | 0 |
| `n_images` | 0 | 0 | 0 |
| `n_list_items` | 16 | 23 | 25 |
| `n_checkboxes` | 0 | 0 | 0 |
| `n_checked` | 0 | 0 | 0 |
| `n_shall` | 3 | 3 | 11 |
| `n_gherkin` | 12 | 23 | 21 |
| `n_scenario_blocks` | 6 | 7 | 7 |
| `n_delta_headers` | 1 | 0 | 0 |
| `n_needs_clarification` | 0 | 0 | 0 |
| `n_todo` | 0 | 0 | 0 |
| `has_ears` | 1 | 1 | 1 |
| `has_gherkin` | 1 | 1 | 1 |
| `has_user_story` | 0 | 0 | 0 |
| `has_requirements` | 1 | 1 | 1 |
| `has_acceptance_criteria` | 0 | 0 | 0 |
| `has_user_scenarios` | 0 | 0 | 0 |
| `has_non_goals` | 0 | 0 | 0 |
| `has_out_of_scope` | 0 | 0 | 0 |
| `has_overview` | 0 | 0 | 0 |
| `has_success_criteria` | 0 | 0 | 0 |
| `has_edge_cases` | 0 | 0 | 0 |
| `has_open_questions` | 0 | 0 | 0 |
| `has_dependencies` | 0 | 1 | 0 |
| `has_purpose` | 0 | 1 | 1 |
| `has_mandatory_marker` | 0 | 0 | 0 |
| `is_tiny` | 0 | 0 | 0 |
| `has_unfilled_placeholder` | 0 | 0 | 0 |
| `has_lorem` | 0 | 0 | 0 |
| `lang` | en | en | en |
| `content_family` | openspec | unknown | unknown |
