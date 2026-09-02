# Setup Checklist — devitsah/devitsah

Everything is generated. Here's what you do by hand, in order.

## 1. Create the profile repo
- Go to `github.com/new`
- Repository name: **devitsah** (exactly your username)
- Public, tick "Add a README"
- Create

## 2. Upload the generated files
Upload these (from this folder) to the **root** of that repo:
- `light.svg`
- `dark.svg`
- `README.md`
- `.github/workflows/snake.yml` (create the folders `.github/workflows/` first, then add the file)

Test the banner: switch your GitHub theme (avatar → Settings → Appearance) and reload your profile — both `light.svg` and `dark.svg` should render.

## 3. Enable Actions permissions (needed for the snake)
Repo → **Settings** (the repo's settings, not your account's) → **Actions** → **General** →
scroll to **Workflow permissions** → select **Read and write permissions** → **Save**.

Then: **Actions** tab → run `Generate Snake Animation` once manually (`Run workflow`). Wait ~1 min
for it to go green — this creates the `output` branch the snake image in the README points to.
Until then, the snake image will show as broken. It regenerates automatically every 12 hours after that.

## 4. (Recommended) Self-host your stats cards
The public `github-readme-stats` / streak-stats instances are shared by thousands of users and
frequently return "API rate limit exceeded." To get a private, always-working instance:

1. **Get a token**: `github.com/settings/tokens` → Tokens (classic) → Generate new token (classic) →
   Note: `readme-stats`, Expiration: No expiration, Scope: `repo` → Generate → copy it immediately.
   Never paste this token into a chat, a public repo, or a website — only into Vercel's environment
   variable field below.
2. **Fork** `github.com/anuraghazra/github-readme-stats`
3. **Vercel**: sign up with GitHub → Hobby (free) plan → Add New Project → import your fork →
   leave build settings as-is
4. Add environment variable `PAT_1` = your token → Deploy → wait for the confetti
5. Copy your instance URL (`your-instance.vercel.app`) and in `README.md` replace
   `github-readme-stats.vercel.app` with your instance URL in the two stats-card image links
   (streak stays on `streak-stats.demolab.com`, that one's already privately rate-limited per-user).

This step is optional — the README works today with the public URLs — but self-hosting means your
cards never go blank from rate limiting.

## 5. Fill in real project links
The Featured Projects table currently links all four rows to `github.com/devitsah`. Once each
project has its own repo, swap in the direct repo URLs.

## 6. Add your resume/portfolio link (optional)
There's room next to the LinkedIn/Email/GitHub badges for a portfolio badge once you have a link —
just say the word and it can be added in the same style.

---

## If something "isn't updating"
Almost always CDN caching, not a bug:
1. Open `https://raw.githubusercontent.com/devitsah/devitsah/main/light.svg?v=999` (the `?v=` bypasses
   the cache) and confirm the change is actually in the file.
2. Check your GitHub theme — dark-mode assets only render in dark mode.
3. Check the Actions tab — is the latest snake run green and after your last push?
4. Then wait — GitHub's CDN typically clears in minutes to a few hours. `Ctrl+Shift+R` clears your
   browser cache but not GitHub's servers.
