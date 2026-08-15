# Project brief

## Purpose

The future product is an owner-operated Chrome extension for preparing and
applying price changes to the operator's own Wildberries catalogue.

## Intended outcomes

- make a proposed price change explicit before it is sent;
- restrict work to products and seller context supplied by the operator;
- show clear success, rejection, and retry-safe outcomes;
- keep repository changes reviewable, reversible, and independent of other
  business repositories.

## Current state

This repository is bootstrap-only. It contains no manifest, browser UI,
background worker, API adapter, credential storage, product logic, deployment,
or live platform call.

## Boundaries

- No secrets or business data are stored in Git.
- No production endpoint is contacted by the baseline.
- Authentication, platform permissions, price-change safeguards, and owner
  acceptance require separate future design and implementation tasks.
- DCP governs repository changes only. It does not deploy or apply a price
  change to Wildberries.
