# Brajesh GitHub Community

A read-only Python project for follower analytics, profile insights, and
automated README reporting using the GitHub REST API and GitHub Actions.

## Features

- Fetch followers and following with complete API pagination.
- Report mutual relationships and one-way relationships.
- Generate `README.md`, `index.html`, `Dataset.json`, and
  `reports/relationships.json`.
- Maintain a deduplicated review queue in `new_users_list.txt`.
- Run locally or on a scheduled/manual GitHub Actions workflow.
- Follow and unfollow code remains available, but is disabled unless
  `--allow-mutations` is explicitly supplied.

## Architecture

`config.py` owns environment and CLI configuration. `github_api.py` provides
Bearer-token authentication, timeouts, API-version headers, pagination, and
explicit API errors. `community.py` contains relationship calculations and
atomic file writes. The small command-line scripts compose these modules, while
`.github/workflows/` runs report generation.

## Installation

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Configuration

Copy `.env.example` to `.env` for reference and export the values in your
shell (the scripts do not load `.env` automatically):

```text
GITHUB_USERNAME=Brajesh31
MY_FOLLOWERS=your_token_here
```

`GITHUB_USERNAME` defaults to `Brajesh31`. `MY_FOLLOWERS` is the preferred
token variable. `GITHUB_TOKEN` is accepted as a local fallback. The token must
belong to the configured account and should have only the permissions required
for the selected operation.

## GitHub token setup

Create a fine-grained personal access token in GitHub settings with read-only
access to public profile data for analytics. Do not paste the token into source
files, notebooks, commit history, logs, or issue comments. For local use, set
`MY_FOLLOWERS` in the process environment. For Actions, add a repository secret
named `MY_FOLLOWERS`; `GITHUB_TOKEN` is reserved for committing workflow output.

## Local execution

```bash
python create_readme.py
python following_my_followers.py
python unfollowing_my_unfollowers.py
python get_random_users.py
python following_new_users.py
```

All commands above are read-only by default. The relationship commands print
candidate lists without changing GitHub. Mutation is deliberately a separate,
explicit action: `python following_my_followers.py --allow-mutations`. Review
the candidates and token permissions before using that flag.

## GitHub Actions

The `create_files.yml` workflow is the only enabled scheduled automation. It
generates reports and commits only when files changed. Run it manually with
`workflow_dispatch`. The other workflows are manual-only and report candidates;
they do not perform follow or unfollow requests.

## Security precautions

- Never commit `.env`, tokens, private keys, or credential files.
- Use least-privilege fine-grained tokens and rotate them if exposed.
- Keep account-mutating operations disabled unless intentionally reviewed.
- Treat generated follower data as public account metadata.

## Project structure

```text
config.py                         shared configuration
github_api.py                     GitHub REST client
community.py                      analytics and atomic persistence helpers
create_readme.py                  report generator
following_my_followers.py         follow-back candidate report
unfollowing_my_unfollowers.py     unfollow candidate report
get_random_users.py               deduplicated review queue
following_new_users.py            queued follow candidate report
Dataset.json                      generated follower profile data
reports/relationships.json        generated relationship report
index.html                        generated browser view
.github/workflows/                GitHub Actions
```
