![Plex ⇄ SIMKL Watchlist Sync](Plex-SIMKL.jpg)

Keep your **Plex Watchlist** and **SIMKL “Plan to Watch”** list aligned.  
This tool compares both lists and applies additions/removals so they end up in sync — safely and predictably.

---

## ✅ Features

- **Two-way sync** between Plex and SIMKL.
- **Plex writes use `plexapi` only** (add/remove). No custom HTTP hacks for writes.
- **Read fallback for Plex**: If `plexapi` cannot read your Plex Watchlist (temporary upstream change),
  the script **falls back to Plex Discover HTTP** for *read-only* watchlist fetching. Writes still use `plexapi`.
- **Clear modes**:
  - **`two-way` (default)** — symmetric sync.  
    - **First run:** *adds only* (seeds a local snapshot to avoid accidental deletes).  
    - **Subsequent runs:** *adds and deletions* both ways, based on deltas vs the snapshot.
  - **`mirror`** — make one side exactly match the other (adds + deletions) using `source_of_truth` (`plex` or `simkl`).
  - **One-way** — turn off bidirectional if you only want Plex → SIMKL.
- **Built-in SIMKL OAuth redirect helper** (`--init-simkl redirect`) to obtain tokens easily.
- **Colored final result**: only the *post-sync* comparison is green/red (“EQUAL/NOT EQUAL”).

---

## 🧩 How it works

1. Read Plex Watchlist (via `plexapi`, or Discover HTTP as a **read-only** fallback) and SIMKL PTW.
2. Build ID sets (IMDB/TMDB/TVDB/slug when available) for stable matching across both services.
3. Compute differences.
4. Apply changes based on your configured mode:
   - **two-way (first run):** add-only on both sides, snapshot saved to `state.json`.
   - **two-way (later runs):** add/remove in both directions using the snapshot to detect deltas.
   - **mirror(plex):** make SIMKL exactly match Plex (add to SIMKL, remove from SIMKL).
   - **mirror(simkl):** make Plex exactly match SIMKL (add/remove in Plex via `plexapi`).

> **Note**: Because Plex write endpoints change occasionally, **writes always go through `plexapi`**. If add/remove fails, upgrade `plexapi` and try again.

---

## 📦 Requirements

- **Python 3.8+**
- Python packages: **`requests`**, **`plexapi`**
- PlexAPI 4.17.1 or higher. Validate if you have the correct version or pip install -U plexapi
- A `config.json` next to the script (auto-created on first run)
- A SIMKL application (client id/secret)
- A Plex account token

Install dependencies (same Python environment you’ll run the script in):

```bash
pip install -U requests plexapi
```

---

## ⚙️ Configuration (`config.json`)

A starter file is created on first run:

```json
{
  "plex": {
    "account_token": ""          // REQUIRED: Your Plex *account* token (not a server token)
  },
  "simkl": {
    "client_id": "",             // REQUIRED: SIMKL API Client ID (from creating an app in SIMKL)
    "client_secret": "",         // REQUIRED: SIMKL API Client Secret
    "access_token": "",          // Leave blank; script fills after OAuth
    "refresh_token": "",         // Leave blank; script fills after OAuth
    "token_expires_at": 0        // Leave as 0; script manages expiry time (unix epoch seconds)
  },
  "sync": {
    "enable_add": true,          // Allow adding missing items
    "enable_remove": true,       // Allow removing extras (used in mirror and two-way w/ deletions)
    "verify_after_write": true,  // Re-read both sides after changes to confirm counts
    "bidirectional": {
      "enabled": true,           // Enable bi-directional sync
      "mode": "two-way",         // "two-way" (union/adds; deletions when state exists) or "mirror"
      "source_of_truth": "plex"  // Used only for "mirror": "plex" or "simkl"
    }
  },
  "runtime": {
    "debug": false               // Set true for verbose logs
  }
}
```

### Keys

- `plex.account_token`: Your Plex account token (see “Getting a Plex token” below).
- `simkl.*`: Credentials and tokens for SIMKL.
- `sync.enable_add` / `sync.enable_remove`: Global toggles for adding/removing.
- `sync.verify_after_write`: Reserved for future verification logic.
- `bidirectional.enabled`: `true` → two-way or mirror; `false` → one-way Plex → SIMKL.
- `bidirectional.mode`:
  - `"two-way"` — symmetric, with state snapshot and real deletions after first run.
  - `"mirror"` — make one side exactly match the other using `source_of_truth`.
- `bidirectional.source_of_truth`: `"plex"` or `"simkl"` (used only in `mirror`).

---

## 🔐 SIMKL OAuth (built-in helper)

This script includes a tiny HTTP server to finish OAuth locally and save tokens to `config.json`.

1. **Create a SIMKL app** at [https://simkl.com](https://simkl.com) → Developers.
2. Set the **redirect URI** to:  
   `http://<YOUR_SERVER_IP>:8787/callback`
3. Run the helper:

```bash
./plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787 --open
```

- Replace `0.0.0.0` with the actual IP of the host/container!
- The script prints an authorization link — open it, grant access, tokens are stored to `config.json`.

---

## 🎟 Getting a Plex account token

1. Open **https://app.plex.tv** and sign in.
2. Open your browser **Developer Tools → Network** tab.
3. Refresh the page and click any request to `app.plex.tv` / API endpoints.
4. Look for the query/header **`X-Plex-Token`** — copy its value.
5. Paste it into `config.json` → `plex.account_token`.

> If you rotate sessions or sign out, your token may change; update `config.json` accordingly.

---

## 🖥️ Usage

Show help (and all examples/flags):

```bash
./plex_simkl_watchlist_sync.py --help
```

Typical flows:

```bash
# First run (creates config.json)
./plex_simkl_watchlist_sync.py

# Initialize SIMKL tokens (local redirect helper on port 8787)
./plex_simkl_watchlist_sync.py --init-simkl redirect --bind 0.0.0.0:8787

# Run a sync (shows banner then [i] logs)
./plex_simkl_watchlist_sync.py --sync

# One-off override of Plex token
./plex_simkl_watchlist_sync.py --sync --plex-account-token YOUR_TOKEN

# Print versions
./plex_simkl_watchlist_sync.py --version
```

### CLI flags

```
--sync                         Run synchronization using config.json
--init-simkl redirect          Start local redirect helper for SIMKL OAuth
--bind HOST:PORT               Bind address for redirect helper (default 0.0.0.0:8787)
--open                         Try to open the SIMKL auth URL locally 
--plex-account-token TOKEN     Override Plex token from config.json once
--debug                        Verbose logging
--version                      Print script and plexapi versions
```

---

## 🔁 Modes in detail

### `two-way` (default)
- **First run:** The script builds `state.json` from the current lists and performs **adds only** on both sides (no deletes) to avoid accidental loss.
- **Next runs:** The script compares current lists to `state.json` and applies **adds and deletions** in both directions.  
  If you **delete** something on SIMKL, it will be removed on Plex; if you **add** something on Plex, it will be added to SIMKL, etc.

> To **re-seed** (e.g., after a major change), delete `state.json` and run again. The first run will be add-only.

### `mirror`
- `source_of_truth: plex` — SIMKL will be made to match Plex (adds + deletions on SIMKL).
- `source_of_truth: simkl` — Plex will be made to match SIMKL (adds + deletions on Plex via `plexapi`).

### One-way
- Set `bidirectional.enabled` to `false` to do Plex → SIMKL only.

---

## 🗃️ Files the script writes

- `config.json` — your configuration + SIMKL tokens.
- `state.json` — local snapshot that enables **real two-way deletions** on subsequent runs.

> If `state.json` is missing, the script treats the run as “first run” and does **adds only**.

---

## 🛠️ Troubleshooting

### `plexapi` not installed or too old
- Error mentions plexapi or an unsupported call. Fix by upgrading in the **same** Python environment:
  ```bash
  pip install -U plexapi
  ```

### Plex watchlist 404 via `plexapi`
- You may see errors like “Section 'watchlist' not found!”.
- The script will **automatically fall back** to **Plex Discover HTTP** *for reading only*.
- **Writes to Plex still require `plexapi`**. If add/remove fails, upgrade `plexapi`.

### Plex add/remove fails (400/404)
- Usually a sign `plexapi` needs an update for the latest Plex Discover endpoints.
- Upgrade:
  ```bash
  pip install -U plexapi
  ```

### SIMKL 401/403
- Your SIMKL access token may be expired or the client credentials are wrong.
- Re-run the OAuth helper and ensure the **redirect URI** in SIMKL matches the one printed by the script.

### Redirect helper unreachable
- Ensure any container/VM port mappings allow inbound to the chosen port (default `8787`).
- If binding `0.0.0.0`, the helper prints a URL you can open from another device on the network.

---

## 🔒 Privacy

- Tokens are stored **locally** in `config.json`.
- The script only talks to **Plex** and **SIMKL**.

---

## 📝 Notes

- **Writes to Plex** always use `plexapi`. No HTTP fallbacks are attempted for add/remove.
- **Only the final post-sync comparison** is colorized **EQUAL/NOT EQUAL** — the initial comparison is an informational pre-check.

---

## 📣 Support

Issues and suggestions are welcome. When reporting problems, include:
- Your Python version and OS
- `plexapi` version (`./plex_simkl_watchlist_sync.py --version`)
- Whether you ran with `--debug`
- Redacted logs that show the failing operation
