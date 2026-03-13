# HEARTBEAT.md

## Periodic Checks (Every ~30min)

### Email Management
- [ ] Check Gmail inbox for new unread emails via `gog gmail search 'in:inbox is:unread' --max 20 --account mosestzu@gmail.com`
- [ ] Flag any urgent/time-sensitive emails (look for: deadlines, meetings, client requests, time-sensitive keywords)
- [ ] Create daily email digest if it's morning (8-10 AM PST) or if requested

### Task Management  
- [ ] Check kanban board (`tasks.json`) for backlog items I can work on
- [ ] If idle and no urgent items, pick up a task and move it to in-progress
- [ ] Update task status and log progress

### Daily Digest Creation
- [ ] **Morning (8-10 AM):** Create daily digest including:
  - New emails summary
  - Calendar events for today
  - Kanban task status
  - Any important notifications or updates
  - Weather if relevant

### Context Monitoring & Auto-Cleanup
- [ ] **Check session token usage** via sessions_list tool
- [ ] **Auto-clean Discord** if discord sessions > 60k tokens:
  - First try: send !cleanall via message tool
  - If that fails: manually delete the session .jsonl file and restart gateway
- [ ] **Auto-restart gateway** if any sessions > 150k tokens
- [ ] **Log cleanup actions** to memory/context-cleanup-log.json
- [ ] **Session file locations**: ~/.openclaw/agents/main/sessions/*.jsonl

### Platform Thread Management  
- [ ] **Discord**: Check for 60+ messages, execute reset at 75+ or natural breakpoint
- [ ] **Slack**: Monitor channel activity, use threading + summaries at 30-50 messages
- [ ] **Any platform**: Watch for natural breakpoints (task completion, topic shifts)
- [ ] Create context summaries before resets

### Proactive Work (When Idle)
- [ ] Work on kanban tasks in priority order
- [ ] Organize and update memory files
- [ ] Check on ongoing projects (git status, etc.)
- [ ] Update documentation if needed
