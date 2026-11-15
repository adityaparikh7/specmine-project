# Checkbox reliability (RQ1)

## Ticked vs unticked, present vs missing

| status | intent | ticked: missing / total | over-claim | unticked: present / total | under-claim |
|---|---|---|---:|---|---:|
| archived | create | 6,150 / 90,715 | 6.8% | 6,534 / 8,165 | 80.0% |
| archived | modify | 4,509 / 102,985 | 4.4% | 7,537 / 8,062 | 93.5% |
| in progress | create | 4,086 / 18,618 | 21.9% | 3,766 / 8,078 | 46.6% |
| in progress | modify | 749 / 15,956 | 4.7% | 5,144 / 5,665 | 90.8% |

## Within-change: changes with both ticked and unticked tasks of one intent

| intent | status | changes | repos | ticked missing | unticked missing | gap (95% CI) |
|---|---|---:|---:|---:|---:|---|
| create | archived | 1,166 | 622 | 6.7% | 17.7% | +11.0 pts (+7.5 to +15.1) |
| create | in progress | 359 | 282 | 27.0% | 54.5% | +27.5 pts (+19.1 to +35.5) |
| modify | archived | 1,604 | 720 | 4.8% | 6.5% | +1.7 pts (-0.4 to +4.2) |
| modify | in progress | 383 | 276 | 6.8% | 10.1% | +3.3 pts (+0.3 to +6.4) |

## Archived changes with no box ticked

| group                                                 |   tasks_md_files |   with_tasks |   with_refs |     refs |   repos |   missing_rate |
|:------------------------------------------------------|-----------------:|-------------:|------------:|---------:|--------:|---------------:|
| archived tasks.md with no box ticked (any task count) |         4426.000 |     3733.000 |    2390.000 |  nan     | nan     |        nan     |
| refs, create                                          |          nan     |      nan     |     nan     | 4787.000 | 487.000 |          0.209 |
| refs, modify                                          |          nan     |      nan     |     nan     | 4060.000 | 553.000 |          0.069 |
