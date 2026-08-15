# Architecture boundaries

## Future logical areas

The product may eventually contain four isolated areas:

1. a Chrome extension surface for selecting an owned item and proposing a
   price;
2. a background boundary for browser lifecycle and request coordination;
3. a typed Wildberries adapter for authenticated owner-authorized operations;
4. validation and audit-friendly result handling that never logs secrets.

These are design boundaries, not implemented components.

## Trust boundaries

- Git and CI contain no Wildberries token, seller data, production response,
  or privileged browser state.
- Future credentials must be supplied at runtime through a separately reviewed
  mechanism and must never be written to repository files or logs.
- Model-free tests use fixtures or fakes and cannot reach a live Wildberries
  endpoint.
- A repository merge changes source only. Deployment, extension installation,
  platform login, and a real price mutation are separate owner-controlled
  actions.

## Change control

The exact DCP repo-only target creates one native task identity, worktree,
branch, and ready PR. A fresh exact-head review, successful `baseline` check,
and global FIFO admission precede the trusted merge. There is no second daemon,
database, scheduler, deploy step, or production controller in this repository.
