# `kiro_files`

Kiro census: requirements/design/tasks artifact metadata under .kiro/specs/.

- **Rows:** 98,574
- **Columns:** 12
- **Used for:** Not used

## Columns

| Column | Type | What it means | Filled in | Different values | Examples |
|---|---|---|---|---|---|
| `id` | BIGINT |  | 100% | 98,574 | 1; 2; 3 |
| `repo_name` | VARCHAR | owner/repo slug (join key to every other layer). | 100% | 12,910 | xiaojilele-glitch/WhyBuddy; MrViincciLeRoy/tendersa; docktermj/senzing-bootcamp-kiro-powers |
| `owner_login` | VARCHAR | repository owner's GitHub login. | 100% | 10,255 | ekicyou; xiaojilele-glitch; MrViincciLeRoy |
| `repo_id` | BIGINT |  | 100% | 12,910 | 1191737450; 1233635906; 1183662298 |
| `file_path` | VARCHAR | path within its repository. | 100% | 90,975 | .kiro/specs/requirements.md; .kiro/specs/design.md; .kiro/specs/tasks.md |
| `file_name` | VARCHAR | file name. | 100% | 270 | requirements.md; design.md; tasks.md |
| `kind` | VARCHAR | artifact kind (kiro: requirements/design/tasks; openspec: proposal.md/design.md/tasks.md/...). | 100% | 5 | requirements; design; tasks |
| `feature` | VARCHAR | the Kiro feature/spec folder name. | 100% | 30,875 | completed; archive; _completed |
| `file_sha` | VARCHAR |  | 100% | 95,936 | 200a6d50b539a3f41fbfc9737f9f8261d65d6eb8; 002c187d15f58b239506adfbd9d83acb5b18a9e8; 07a72b20dcb3906a33cfb7033c09a0f6528deea4 |
| `html_url` | VARCHAR |  | 100% | 98,574 | https://github.com/0-TeXaS-0/AI-FOR-BHARAT/blob/8af972117d3af54a4ea1c4c659602e2f2a34250f/.kiro/specs/multilingual-mandi/ …; https://github.com/0-TeXaS-0/AI-FOR-BHARAT/blob/8af972117d3af54a4ea1c4c659602e2f2a34250f/.kiro/specs/multilingual-mandi/ …; https://github.com/0-TeXaS-0/AI-FOR-BHARAT/blob/8af972117d3af54a4ea1c4c659602e2f2a34250f/.kiro/specs/multilingual-mandi/ … |
| `git_url` | VARCHAR |  | 100% | 98,501 | https://api.github.com/repositories/1069013434/git/blobs/6ccbd02abea1063c0406d5f067e9c3011f13745b; https://api.github.com/repositories/1068052532/git/blobs/cba4f8f0e0f59c4bd97719677df6471a0802e8bd; https://api.github.com/repositories/1007807090/git/blobs/57d3d08fe726dcdc4b3aa5d0f6173e554d8407e8 |
| `fetched_at` | VARCHAR |  | 100% | 1,267 | 2026-07-22T17:08:11Z; 2026-07-22T17:08:13Z; 2026-07-22T17:08:16Z |

## Three sample rows

| Column | Row 1 | Row 2 | Row 3 |
|---|---|---|---|
| `id` | 8130 | 9205 | 11774 |
| `repo_name` | gerardoojeda47/rutasapp | jasonwadsworth/hallway-track | yuneco/webgl-paint-poc |
| `owner_login` | gerardoojeda47 | jasonwadsworth | yuneco |
| `repo_id` | 1004518251 | 1093218731 | 1024332179 |
| `file_path` | .kiro/specs/distribucion-app-qr/requirements.md | .kiro/specs/connection-request-metadata/design.md | .kiro/specs/webgl-symmetry-paint-poc/requirements.md |
| `file_name` | requirements.md | design.md | requirements.md |
| `kind` | requirements | design | requirements |
| `feature` | distribucion-app-qr | connection-request-metadata | webgl-symmetry-paint-poc |
| `file_sha` | 1179bebfabad56609800d2d355adf76f683f9007 | 7de063a05027ab2380d7db75aa8cc298d781549d | ecd46f2ebdc102e9679b484ba884557db27b42b5 |
| `html_url` | https://github.com/gerardoojeda47/rutasapp/blob/2d88e46ff5ff51ff6f0660bf4d13d6f8d4092cf5/.kiro/specs/distribucion-app-qr … | https://github.com/jasonwadsworth/hallway-track/blob/04d77f2243d5d66fb44f049013f8bcf172d13c36/.kiro/specs/connection-req … | https://github.com/yuneco/webgl-paint-poc/blob/92b3236abd9447e169fc8a2586c10ebb44876f34/.kiro/specs/webgl-symmetry-paint … |
| `git_url` | https://api.github.com/repositories/1004518251/git/blobs/1179bebfabad56609800d2d355adf76f683f9007 | https://api.github.com/repositories/1093218731/git/blobs/7de063a05027ab2380d7db75aa8cc298d781549d | https://api.github.com/repositories/1024332179/git/blobs/ecd46f2ebdc102e9679b484ba884557db27b42b5 |
| `fetched_at` | 2026-07-22T17:10:28Z | 2026-07-22T17:10:49Z | 2026-07-22T17:11:42Z |
