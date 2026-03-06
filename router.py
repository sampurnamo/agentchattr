"""Message routing based on @mentions with per-channel loop guard."""

import re


class Router:
    def __init__(self, agent_names: list[str], alias_map: dict[str, str] | None = None, default_mention: str = "both",
                 max_hops: int = 4):
        self.agent_names = set(n.lower() for n in agent_names)
        self.alias_map = {k.lower(): v.lower() for k, v in (alias_map or {}).items()}
        for name in self.agent_names:
            self.alias_map.setdefault(name, name)
        self.default_mention = default_mention
        self.max_hops = max_hops
        # Per-channel state: { channel: { hop_count, paused, guard_emitted } }
        self._channels: dict[str, dict] = {}
        self._build_pattern()

    def _get_ch(self, channel: str) -> dict:
        if channel not in self._channels:
            self._channels[channel] = {
                "hop_count": 0,
                "paused": False,
                "guard_emitted": False,
            }
        return self._channels[channel]

    def _build_pattern(self):
        names = "|".join(re.escape(n) for n in sorted(self.alias_map.keys(), key=len, reverse=True))
        self._mention_re = re.compile(
            rf"@({names}|both|all)\b", re.IGNORECASE
        )

    def normalize_name(self, name: str) -> str:
        key = (name or "").strip().lower()
        return self.alias_map.get(key, key)

    def parse_mentions(self, text: str) -> list[str]:
        mentions = set()
        for match in self._mention_re.finditer(text):
            name = match.group(1).lower()
            if name in ("both", "all"):
                mentions.update(self.agent_names)
            else:
                canonical = self.normalize_name(name)
                if canonical in self.agent_names:
                    mentions.add(canonical)
        return list(mentions)

    def _is_agent(self, sender: str) -> bool:
        return self.normalize_name(sender) in self.agent_names

    def get_targets(self, sender: str, text: str, channel: str = "general") -> list[str]:
        """Determine which agents should receive this message."""
        ch = self._get_ch(channel)
        mentions = self.parse_mentions(text)

        if not self._is_agent(sender):
            # Human message resets hop counter and unpauses
            ch["hop_count"] = 0
            ch["paused"] = False
            ch["guard_emitted"] = False
            if not mentions:
                if self.default_mention in ("both", "all"):
                    return list(self.agent_names)
                elif self.default_mention == "none":
                    return []
                return [self.default_mention]
            return mentions
        else:
            # Agent message: blocked while loop guard is active
            if ch["paused"]:
                return []
            # Only route if explicit @mention
            if not mentions:
                return []
            ch["hop_count"] += 1
            if ch["hop_count"] > self.max_hops:
                ch["paused"] = True
                return []
            # Don't route back to self
            sender_key = self.normalize_name(sender)
            return [m for m in mentions if m != sender_key]

    def continue_routing(self, channel: str = "general"):
        """Resume after loop guard pause."""
        ch = self._get_ch(channel)
        ch["hop_count"] = 0
        ch["paused"] = False
        ch["guard_emitted"] = False

    def is_paused(self, channel: str = "general") -> bool:
        return self._get_ch(channel)["paused"]

    def is_guard_emitted(self, channel: str = "general") -> bool:
        return self._get_ch(channel)["guard_emitted"]

    def set_guard_emitted(self, channel: str = "general"):
        self._get_ch(channel)["guard_emitted"] = True

    def update_agents(self, names: list[str]):
        """Replace the agent name set and rebuild the mention regex."""
        self.agent_names = set(n.lower() for n in names)
        for name in self.agent_names:
            self.alias_map.setdefault(name, name)
        self._build_pattern()
