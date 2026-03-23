# Security

- Never commit secrets like `keys.json`, `.env`, or tokens.
- Treat `allow_insecure_coding` and `!newAction` as high-risk features.
- Avoid destructive filesystem or git actions unless explicitly requested.
- Do not overwrite unrelated user changes in a dirty working tree.
- Be cautious with runtime changes that affect process shutdown, restart, or socket connections.
