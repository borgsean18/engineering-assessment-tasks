# Candidate materials

Everything in this folder is **safe to share with candidates**. It does not contain scoring
rubrics, interviewer scripts, or calibration notes.

## What you receive

| Resource                                  | Purpose                                                          |
| ----------------------------------------- | ---------------------------------------------------------------- |
| [Business glossary](business-glossary.md) | Construction & project-controls terms used in briefs and the app |
| [`base-app/`](base-app/README.md)         | Runnable **Project Controls Hub** codebase to extend             |
| [`briefs/`](briefs/README.md)             | Your take-home brief (pick one matching your role)               |

## Quick start

```bash
cd base-app
docker compose -f infra/docker-compose.yml up --build --watch   # API on :8000
yarn install && yarn nx serve hub                        # UI on :4200
```

API without Docker: see [base-app README](base-app/README.md#running-locally-summary).

## Take-home task rules (summary)

- **Time cap:** max 90 minutes (stop at 90 min and document what's left in `SOLUTION.md`)
- **Submit:** zip + `SOLUTION.md` (decisions, trade-offs, **AI/tooling disclosure**)
- **Tests:** proportional to scope; quality over quantity
- **AI:** allowed if disclosed; you must explain and change your code in live sessions
- **Marked:** your take-home is scored as part of the application, alongside the live sessions

## Roles covered

| Track                | Brief                                                            |
| -------------------- | ---------------------------------------------------------------- |
| Frontend             | [briefs/mid/frontend-mid.md](briefs/mid/frontend-mid.md)         |
| Backend              | [briefs/mid/backend-mid.md](briefs/mid/backend-mid.md)           |
| Full-stack (FE-lean) | [briefs/mid/fullstack-fe-mid.md](briefs/mid/fullstack-fe-mid.md) |
| Full-stack (BE-lean) | [briefs/mid/fullstack-be-mid.md](briefs/mid/fullstack-be-mid.md) |

## What happens next

After your take-home is reviewed, you may be invited to live sessions (code review, refinement,
and pair programming). Your recruiter will send scheduling details when sessions are confirmed.
