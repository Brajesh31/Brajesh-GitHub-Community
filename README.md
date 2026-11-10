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

All three account automations are enabled for this project with conservative
limits:

```text
AUTO_FOLLOW_ENABLED=true
AUTO_FOLLOW_BACK_ENABLED=true
AUTO_UNFOLLOW_ENABLED=true
DRY_RUN=false
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
| `AUTO_FOLLOW_ENABLED` | `true` | Allow discovered-account follows |
| `AUTO_FOLLOW_BACK_ENABLED` | `true` | Allow follow-back actions |
| `AUTO_UNFOLLOW_ENABLED` | `true` | Allow non-mutual unfollows |
| `DRY_RUN` | `false` | Set true to simulate without API mutations |
| `MAX_FOLLOW_ACTIONS` | `5` | Per-execution follow/unfollow cap |
| `MAX_UNFOLLOW_ACTIONS` | `5` | Per-execution unfollow cap |
| `MAX_FOLLOW_ACTIONS_PER_DAY` | `20` | Daily follow cap |
| `MAX_UNFOLLOW_ACTIONS_PER_DAY` | `20` | Daily unfollow cap |
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

Mutation scripts require the relevant `AUTO_*` flag, `DRY_RUN=false`, and a
token with Followers write permission. Set `DRY_RUN=true` when manually
testing without API mutations. The hidden legacy `--allow-mutations` switch
enables all operations for deliberate local testing.

## GitHub Actions

Separate workflows exist for discovery, new-account follow processing,
follow-back, report generation, non-mutual review, Pages deployment, and
validation. Each supports manual dispatch; scheduled mutation workflows set
the requested automation flags to enabled with `DRY_RUN=false`. Workflows use `MY_FOLLOWERS` only for
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

<!-- COMMUNITY_REPORT_START -->
## Generated community report

Community analytics for [Brajesh31](https://github.com/Brajesh31).

## Community statistics

- Followers: **29**
- Following: **108**
- Mutual: **29**
- Followers Not Followed: **0**
- Following Not Following Back: **79**
- Discovered Candidates: **55**
- Successfully Followed: **69**
- Awaiting Review: **55**
- Updated: `2026-11-10T09:30:07+00:00`

## Followers

<a href="https://github.com/Abhishek123691"><img src="https://avatars.githubusercontent.com/u/217572952?v=4" alt="Abhishek123691" height="50" width="50"></a>
<a href="https://github.com/CyberFocus2410"><img src="https://avatars.githubusercontent.com/u/221118698?v=4" alt="CyberFocus2410" height="50" width="50"></a>
<a href="https://github.com/Deynn0"><img src="https://avatars.githubusercontent.com/u/219535114?v=4" alt="Deynn0" height="50" width="50"></a>
<a href="https://github.com/Divyanshgupta13"><img src="https://avatars.githubusercontent.com/u/172985044?v=4" alt="Divyanshgupta13" height="50" width="50"></a>
<a href="https://github.com/DivyomSharma"><img src="https://avatars.githubusercontent.com/u/172122448?v=4" alt="DivyomSharma" height="50" width="50"></a>
<a href="https://github.com/Himanshu12315603"><img src="https://avatars.githubusercontent.com/u/150218275?v=4" alt="Himanshu12315603" height="50" width="50"></a>
<a href="https://github.com/MalcomVie"><img src="https://avatars.githubusercontent.com/u/222227281?v=4" alt="MalcomVie" height="50" width="50"></a>
<a href="https://github.com/MizukiSonoko"><img src="https://avatars.githubusercontent.com/u/6281583?v=4" alt="MizukiSonoko" height="50" width="50"></a>
<a href="https://github.com/NovaDhruv15"><img src="https://avatars.githubusercontent.com/u/184974534?v=4" alt="NovaDhruv15" height="50" width="50"></a>
<a href="https://github.com/Princemaurya25"><img src="https://avatars.githubusercontent.com/u/173058073?v=4" alt="Princemaurya25" height="50" width="50"></a>
<a href="https://github.com/Raj1234ed"><img src="https://avatars.githubusercontent.com/u/239550125?v=4" alt="Raj1234ed" height="50" width="50"></a>
<a href="https://github.com/RitikkumarAI"><img src="https://avatars.githubusercontent.com/u/145904770?v=4" alt="RitikkumarAI" height="50" width="50"></a>
<a href="https://github.com/Vinit279"><img src="https://avatars.githubusercontent.com/u/196689444?v=4" alt="Vinit279" height="50" width="50"></a>
<a href="https://github.com/asawaaarav09"><img src="https://avatars.githubusercontent.com/u/219246546?v=4" alt="asawaaarav09" height="50" width="50"></a>
<a href="https://github.com/b28089840-svg"><img src="https://avatars.githubusercontent.com/u/239539539?v=4" alt="b28089840-svg" height="50" width="50"></a>
<a href="https://github.com/b90649577-web"><img src="https://avatars.githubusercontent.com/u/225809329?v=4" alt="b90649577-web" height="50" width="50"></a>
<a href="https://github.com/boldotter921"><img src="https://avatars.githubusercontent.com/u/331097667?v=4" alt="boldotter921" height="50" width="50"></a>
<a href="https://github.com/cg2102005-dotcom"><img src="https://avatars.githubusercontent.com/u/239552832?v=4" alt="cg2102005-dotcom" height="50" width="50"></a>
<a href="https://github.com/chirag-g210"><img src="https://avatars.githubusercontent.com/u/190064639?v=4" alt="chirag-g210" height="50" width="50"></a>
<a href="https://github.com/code-market-software"><img src="https://avatars.githubusercontent.com/u/100116238?v=4" alt="code-market-software" height="50" width="50"></a>
<a href="https://github.com/code-with-abhi-i5"><img src="https://avatars.githubusercontent.com/u/195516410?v=4" alt="code-with-abhi-i5" height="50" width="50"></a>
<a href="https://github.com/ganesh112389-spec"><img src="https://avatars.githubusercontent.com/u/239596832?v=4" alt="ganesh112389-spec" height="50" width="50"></a>
<a href="https://github.com/omasanori"><img src="https://avatars.githubusercontent.com/u/167209?v=4" alt="omasanori" height="50" width="50"></a>
<a href="https://github.com/omgupta9219"><img src="https://avatars.githubusercontent.com/u/158093368?v=4" alt="omgupta9219" height="50" width="50"></a>
<a href="https://github.com/raj113422k-create"><img src="https://avatars.githubusercontent.com/u/239600717?v=4" alt="raj113422k-create" height="50" width="50"></a>
<a href="https://github.com/sanskaryo"><img src="https://avatars.githubusercontent.com/u/104834389?v=4" alt="sanskaryo" height="50" width="50"></a>
<a href="https://github.com/shivamtiwari432"><img src="https://avatars.githubusercontent.com/u/146664085?v=4" alt="shivamtiwari432" height="50" width="50"></a>
<a href="https://github.com/tech-dev-club"><img src="https://avatars.githubusercontent.com/u/239598714?v=4" alt="tech-dev-club" height="50" width="50"></a>
<a href="https://github.com/unbraind"><img src="https://avatars.githubusercontent.com/u/1153461?v=4" alt="unbraind" height="50" width="50"></a>

<!-- COMMUNITY_REPORT_END -->





