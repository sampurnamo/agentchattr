# agentchattr - Quick Commands Guide (Windows / PowerShell)

This is a quick reference for starting the server and agents, opening the UI, and keeping the room consistent.

## Load the Commands
If you just updated your profile, reload it in a PowerShell session:

```powershell
. $PROFILE.CurrentUserAllHosts
```

## Start / Stop the Server
Use the server helper from anywhere:

```powershell
ac-server start
ac-server status
ac-server stop
ac-server restart
ac-revive
```

## Start Agents (auto-starts server if needed)
Single agent:

```powershell
ac-meera -Open
ac-ishika -Open
ac-rashmika -Open
```

All three:

```powershell
ac-all -Open
```

Recover all three if they dropped offline:

```powershell
ac-revive -Open
```

Notes:
- `-Open` opens the UI at `http://127.0.0.1:8300/`.
- Omit `-Open` if you already have the tab open.

## Direct Command Names (long form)
Same as the aliases above:

```powershell
Agentchattr-Meera -Open
Agentchattr-Ishika -Open
Agentchattr-Rashmika -Open
Agentchattr-All -Open
Agentchattr-Server start
```

## If Agents Look Offline
- Confirm the server is running: `ac-server status`.
- Restart agent(s): `ac-meera`, `ac-ishika`, `ac-rashmika`.
- Hard refresh the UI: `Ctrl+F5`.

## Rejoin + Idle Presence
- To bring agents back immediately: run `ac-ishika` and `ac-rashmika` (and `ac-meera` if needed).
- If a message says "appears offline — message queued", start that agent wrapper and it will consume queued messages.
- Fast one-shot recovery: `ac-revive` (use `ac-revive -KeepExisting` if you only want restart+rejoin without killing existing wrappers first).
- Idle timeout is controlled in `config.toml`:
```toml
[presence]
timeout_seconds = 600
heartbeat_seconds = 30
```
- After changing `config.toml`, run `ac-server restart`.

---

If you want this guide in a different location or format, tell me and I'll adjust it.
