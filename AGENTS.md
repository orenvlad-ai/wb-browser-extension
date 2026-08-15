# Repository rules

This public repository is the isolated, repo-only home for a future Chrome
extension that changes prices only for products owned by its operator.

- The bootstrap commit is the sole permitted direct `main` commit. Every later
  change starts through DCP target `wb-price-extension`, profile `repo-only`.
- DCP is the only merge controller. A worker creates one scoped branch and one
  ready PR; the trusted DCP reviewer, FIFO admission lease, and terminal merger
  own review and merge. Do not merge manually or push feature changes to
  `main`.
- Work only inside the current native DCP worktree. Do not read or mutate
  `wb-core`, `dev-control-plane`, `dcp-orchestrator`, production, secrets, or
  any other repository.
- Keep changes task-scoped. Exact task replay is idempotent; conflicting replay
  fails closed. Do not create extra branches, worktrees, PRs, services, queues,
  watchers, or release paths.
- The required check is exactly `baseline`. It must stay model-free and must
  not call Wildberries or require secrets.
- Never commit tokens, credentials, product data, production endpoints, or
  telemetry. Do not call a live Wildberries API from tests or automation.
- This repository has no deploy, Release Train, server mutation, or production
  apply path. Product rollout and manual owner acceptance are separate future
  decisions.

Technical terminal state for a DCP repository task is `MERGED`; it is not
owner acceptance.
