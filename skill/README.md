# VectorClaw ClawHub Skill

This folder contains the ClawHub skill definition for VectorClaw.

## Files

- `SKILL.md` - Main skill definition with metadata and documentation

## Publishing

```bash
# Login to ClawHub (one-time)
npx clawhub login

# Publish the skill
npx clawhub publish ./skill \
  --slug vectorclaw-mcp \
  --name "VectorClaw MCP" \
  --version 1.0.0 \
  --tags "latest,robotics,vector,mcp"
```

## Testing Locally

Before publishing, test the skill works with your OpenClaw installation by:

1. Installing the vectorclaw-mcp package
2. Adding the MCP server config to your mcporter.json
3. Verifying tools work through OpenClaw

## Updates

When updating the skill:
1. Edit `SKILL.md`
2. Increment version in publish command
3. Add `--changelog` notes for significant changes
