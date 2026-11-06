# Brajesh GitHub Community

A Python-based GitHub community automation system for follower analytics,
profile insights, candidate discovery, guarded follow/follow-back/unfollow
operations, and generated README/dashboard reporting.

## Architecture

- `config.py`: one conservative configuration model and environment parser.
- `github_api.py`: Bearer-authenticated REST client with pagination, bounded
  retries, rate-limit handling, status-specific errors, identity checks, and
  mutation-permission checks.
- `community.py`: relationship calculations, atomic JSON/text writes, action
  history, whitelist/blacklist protection, waiting periods, dry-run, and
  action limits.
- Command scripts: discovery, new-account following, follow-back, unfollow
  review, and report generation.
- `data/`: candidates, follow history, unfollow history, and action history.
- `reports/`: relationship, statistics, and action-summary JSON consumed by
  both README and the static dashboard.
- `index.html`, `src/main.js`, `src/style.css`: credential-free responsive
  GitHub Pages dashboard.

## Features

Follower and following pagination, mutual/non-mutual analysis, duplicate-safe
candidate discovery, persistent history, blacklist/whitelist protection,
minimum unfollow waiting period, conservative daily/action limits, dry-run
simulation, and generated community reports are included.

All account mutations are disabled by default:

```text
AUTO_FOLLOW_ENABLED=false
AUTO_FOLLOW_BACK_ENABLED=false
AUTO_UNFOLLOW_ENABLED=false
DRY_RUN=true
```

Changing code or workflow values does not bypass GitHub permissions or
anti-abuse restrictions. Review candidates before intentionally enabling a
mutation and keep limits conservative.

## Setup

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
```

Copy `.env.example` to a secure environment configuration. The scripts read
environment variables; they do not load `.env` automatically.

### Configuration flags

| Variable | Default | Purpose |
|---|---:|---|
| `GITHUB_USERNAME` | `Brajesh31` | Authenticated account |
| `MY_FOLLOWERS` | unset | Fine-grained token |
| `AUTO_DISCOVERY_ENABLED` | `true` | Discover public candidates |
| `AUTO_FOLLOW_ENABLED` | `false` | Allow discovered-account follows |
| `AUTO_FOLLOW_BACK_ENABLED` | `false` | Allow follow-back actions |
| `AUTO_UNFOLLOW_ENABLED` | `false` | Allow non-mutual unfollows |
| `DRY_RUN` | `true` | Record/report without API mutations |
| `MAX_FOLLOW_ACTIONS` | `5` | Per-execution follow/unfollow cap |
| `MAX_FOLLOW_ACTIONS_PER_DAY` | `20` | Daily follow cap |
| `MIN_UNFOLLOW_WAIT_DAYS` | `14` | Required age of a recorded follow |
| `WHITELIST_PATH` | `whitelist.txt` | Never automatically unfollow |
| `BLACKLIST_PATH` | `blacklist.txt` | Never automatically follow/discover |
| `DATA_DIR` | `data` | Persistent history directory |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## Token permissions and security

Create a GitHub fine-grained personal access token belonging to `Brajesh31`.
Followers **read** permission is sufficient for analytics and discovery.
Followers **write** permission is required for follow and unfollow operations.
Store it locally only in `MY_FOLLOWERS`, or as the GitHub Actions secret with
that exact name. `GITHUB_TOKEN` is separate and is used only for repository
commits and Pages deployment. Never commit a real token, print one in logs, or
paste one into source files. Rotate a token immediately if exposed.

## Local commands

```bash
python get_random_users.py
python following_new_users.py
python following_my_followers.py
python unfollowing_my_unfollowers.py
python create_readme.py
pytest -q
```

Mutation scripts remain simulation-only until both the relevant `AUTO_*` flag
is enabled and `DRY_RUN=false`. The hidden legacy `--allow-mutations` switch
enables all operations for deliberate local testing, but workflow files never
use it.

## GitHub Actions

Separate workflows exist for discovery, new-account follow processing,
follow-back, report generation, non-mutual review, Pages deployment, and
validation. Each supports manual dispatch; scheduled mutation workflows set
the safety flags to disabled/dry-run. Workflows use `MY_FOLLOWERS` only for
the API and `GITHUB_TOKEN`/workflow permissions for repository writes.

Generated commits use `fetch-depth: 0`, `git pull --rebase`, no-op checks, and
concurrency groups to preserve remote changes and avoid the previous
`fetch first` failure. They never force-push.

## GitHub Pages

In repository **Settings → Pages**, choose **GitHub Actions** as the source.
The `pages.yml` workflow deploys the static dashboard manually or after a
successful community report. It uploads only the static public dashboard and
generated JSON; no token or private configuration is included.

## Project files

See `data/`, `reports/`, `whitelist.txt`, `blacklist.txt`, `.github/workflows/`,
and the command modules described above. `Dataset.json` contains public
follower profile metadata only.
