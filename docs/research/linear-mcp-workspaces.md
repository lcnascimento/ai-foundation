# Linear MCP with one workspace per Project

Research for Linear issue AI-23. Context: ADR-0003 gives each Project its own Linear workspace; ADR-0001 says MCP servers come from the official plugin (`linear@claude-plugins-official`) unless own configuration is needed. Question: how does the Linear MCP reach the right workspace in each Project?

Researched 2026-10-08 against Claude Code 2.1.286. Every claim cites its source. **[verified locally]** marks something observed on this machine. **[unverified]** marks an inference with no primary source behind it.

## TL;DR

- One Linear MCP auth (an OAuth grant or an API key) reaches **one workspace**.
- Claude Code stores each OAuth token under a key built from the **server name plus a hash of `{type, url, headers}`**. The key does not depend on scope or on the project directory. The official plugin has the same name and URL in every Project, so **all Projects share one token, and therefore one workspace**. Switching workspace means clearing auth and signing in again, and that changes the workspace for every Project.
- A per-Project definition fixes this, because a definition that differs gives a different token key. The Project ships its own `.mcp.json`, which is the exception ADR-0001 allows (own configuration is needed). It can authenticate in two ways:
  - **OAuth**: a definition that differs per Project. Same URL, with a per-Project marker header or server name.
  - **API key**: a per-workspace personal API key sent as `Authorization: Bearer ${LINEAR_API_KEY}`.
- **Cloud sessions do not install plugins declared by the repo**, so the official plugin never reaches claude.ai/code. A cloud session does load the repo's committed `.mcp.json`. A **claude.ai connector** is account-wide, so it reaches one workspace.
- **Recommendation**: each Project commits a `.mcp.json` with a server named `linear` that uses the API key header, and the key is supplied per Project. The details are under "Recommended Project setup".

## 1. Does Linear's OAuth authorize one workspace per connection?

Yes.

- Linear's MCP docs: "Each workspace needs its own separate authentication context". For `mcp-remote`, they suggest one config dir per workspace (`MCP_REMOTE_CONFIG_DIR=~/.mcp-auth/workspace-a npx mcp-remote https://mcp.linear.app/mcp`). For clients that store their own auth, "check the client documentation for workspace-switching options". ([linear.app/docs/mcp](https://linear.app/docs/mcp))
- Linear's OAuth docs: `prompt=consent` "can be useful if you want to give users the opportunity to connect multiple workspaces". This implies that each grant is tied to the workspace picked on the consent screen. ([linear.app/developers/oauth-2-0-authentication](https://linear.app/developers/oauth-2-0-authentication))
- The MCP server also accepts `Authorization: Bearer <token>` with "OAuth token and API keys directly … instead of using the interactive authentication flow", for example for read-only API keys. ([linear.app/docs/mcp](https://linear.app/docs/mcp))
- Personal API keys are created under Settings → Account → Security & access ([linear.app/developers/graphql](https://linear.app/developers/graphql)). That page does not say how the keys are scoped. Third-party docs say a key "is scoped to the workspace you are currently logged into when creating it" ([docs.sim.ai](https://docs.sim.ai/integrations/linear-service-account)). **[secondary source, not confirmed by Linear]**

Endpoints: `https://mcp.linear.app/mcp` (Streamable HTTP), `/mcp/readonly`, and `/sse` (deprecated). ([linear.app/docs/mcp](https://linear.app/docs/mcp))

## 2. Where does Claude Code store the token?

- Docs: tokens live "in your system keychain (macOS) or a credentials file, not in your config". They "are stored per endpoint, so when you authenticate a definition in one project, you still need to sign in separately in a project where a different definition loads". "Clear authentication" in `/mcp` revokes the token. ([code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp))
- **[verified locally]** The macOS keychain item `Claude Code-credentials` holds a `mcpOAuth` map. The official plugin's entry has the key `plugin:linear:linear|638130d5ab3558f4` and stores `serverName` and `serverUrl=https://mcp.linear.app/mcp`. The suffix is exactly the first 16 hex characters of `sha256('{"type":"http","url":"https://mcp.linear.app/mcp","headers":{}}')`. So the key is **server name + hash of type, URL and headers**. It has no project path or scope in it.
  - The key format is undocumented. **[unverified]** We do not know whether `headers` is hashed before or after `${VAR}` expansion.
- So the answer is: per server name plus definition, global to the machine. A definition that is identical in two Projects shares one token. A definition that differs, by name or by headers, gets its own token.

## 3. Can concurrent sessions in different Projects use different workspaces?

- **With the official plugin alone: no.** Its definition is the same everywhere: the server is registered as `plugin:linear:linear` ([code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)), and the plugin's `.mcp.json` is `{"linear": {"type": "http", "url": "https://mcp.linear.app/mcp"}}` (`external_plugins/linear` in anthropics/claude-plugins-official, read from the local marketplace clone). Every Project therefore reads the same keychain entry, and re-authenticating in one Project switches the workspace for all of them, including sessions already running.
- **With a definition that differs per Project: yes.** Each definition has its own token key, so sessions in different Projects run concurrently with no re-authentication. With API-key headers there is no stored OAuth token at all, and each session sends its own key.

## 4. Can configuration select the workspace?

Linear has no workspace parameter in its URL or headers. The docs only mention separate auth contexts ([linear.app/docs/mcp](https://linear.app/docs/mcp)). The workspace is chosen by whichever credential the session sends. Claude Code offers three ways to supply a credential per Project ([code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)):

- **Static headers with env expansion**: `"headers": {"Authorization": "Bearer ${LINEAR_API_KEY}"}`.
  - `${VAR}` and `${VAR:-default}` expand in `url` and `headers`.
  - An unset variable stays as literal text, with a warning in `claude mcp list`.
  - Only a fixed list of credential names, such as `ANTHROPIC_API_KEY` and `NPM_TOKEN`, is blanked. `LINEAR_API_KEY` is not on that list.
- **`headersHelper`**: a command that prints headers as JSON. It runs on every connect, with `CLAUDE_CODE_MCP_SERVER_NAME` and `CLAUDE_CODE_MCP_SERVER_URL` set. For a project `.mcp.json`, it runs only after the project trust dialog. It could read a per-Project key from the keychain.
- **Scope precedence**: local, then project, then user, then plugin, then claude.ai connector.
  - "Plugins and connectors" are matched to the scopes "by endpoint". So a Project `.mcp.json` pointing at `https://mcp.linear.app/mcp` **suppresses the official plugin's server as a duplicate**, and the plugin can stay installed without conflict.
  - Fields are not merged across sources.
  - Duplicate detection ignores only case, default port and a trailing slash. A different path or query string makes a separate server.

**Does this need our own `.mcp.json`?** Yes. The official plugin's definition has a fixed name and URL and no headers, so per-Project selection is impossible through it. This is the "own configuration is needed" exception in ADR-0001. Two consequences:

- Tool names change from `mcp__plugin_linear_linear__*` to `mcp__<server-name>__*` ([code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp)). `docs/agents/issue-tracker.md` currently hard-codes `mcp__plugin_linear_linear__*`. A stable server name across Projects, such as `linear`, keeps the tool names stable.
- The `.mcp.json` must live in the Project repo, not in a Marketplace plugin. A plugin's definition is the same in every Project, so it would bring back the shared token, unless it reads a per-Project env var.

## 5. Cloud sessions (claude.ai/code) and claude.ai connectors

- **Plugins**: "A cloud session doesn't install the plugins a repository turns on under `enabledPlugins`". Plugins enabled only in user settings don't carry over either. MCP servers added at local or user scope don't carry over. **The repo's `.mcp.json` does load** in a session with one repository. ([code.claude.com/docs/en/cloud-environments](https://code.claude.com/docs/en/cloud-environments), "What carries over from your setup")
- **Secrets**: environment variables on a cloud environment are readable by anyone who uses that environment. On Pro and Max plans, a **network secret** stores a key, such as an `Authorization: Bearer` header, for the hosts you list, and the agent proxy attaches it outside the VM. Team and Enterprise plans don't have network secrets yet. ([code.claude.com/docs/en/cloud-environments](https://code.claude.com/docs/en/cloud-environments))
  - **[unverified]** We have not tested whether the agent proxy attaches a network secret to MCP HTTP traffic from a repo `.mcp.json`. It should, since that traffic leaves the VM like any other request. An environment variable read through `${LINEAR_API_KEY}` is the path the docs do cover.
- **Picking the environment per Project**: `remote.defaultEnvironmentId` picks the environment for CLI-started cloud sessions, and a repo's project settings can set it ([code.claude.com/docs/en/cloud-environments](https://code.claude.com/docs/en/cloud-environments), "Select an environment from the CLI"). One environment per Project, each holding that workspace's key, therefore fits. In the web UI the user picks the environment by hand.
- **OAuth in the cloud**: the docs mention sessions waiting "to sign in to an MCP server" ([code.claude.com/docs/en/claude-code-on-the-web](https://code.claude.com/docs/en/claude-code-on-the-web), "Environment expired"). **[unverified]** We don't know whether such a sign-in persists across sessions. Treat cloud OAuth as one sign-in per session.
- **claude.ai connectors**:
  - Connectors are added at claude.ai/customize/connectors and appear in Claude Code only under a claude.ai subscription login.
  - In cloud sessions their traffic goes through Anthropic's servers.
  - They have the lowest precedence and are deduped by endpoint against local definitions.
  - They can be turned off with `disableClaudeAiConnectors` or `ENABLE_CLAUDEAI_MCP_SERVERS=false`, and blocked one by one with `deniedMcpServers`.

  ([code.claude.com/docs/en/mcp](https://code.claude.com/docs/en/mcp), [cloud-environments](https://code.claude.com/docs/en/cloud-environments))

  A connector belongs to the claude.ai account, not the repo, so a Linear connector reaches one workspace in every session. **[unverified]** We don't know whether claude.ai allows several custom connectors for the same URL, each authorized to a different workspace. Even if it does, they would not be bound to a Project.

## Options compared

| Option | Per-Project workspace (local) | Concurrent | Cloud | Cost |
| - | - | - | - | - |
| Official plugin only (status quo) | No, one global token | No | Plugin not installed | none |
| Project `.mcp.json`, OAuth, per-Project server name (`linear-<project>`) | Yes | Yes | One sign-in per session **[unverified]** | Tool names differ per Project, so skills can't hard-code them |
| Project `.mcp.json`, OAuth, name `linear` + marker header (`X-Project: <project>`) | Yes, because headers change the hash | Yes | Same as above | Relies on the undocumented key format, and Linear must ignore the extra header **[unverified]** |
| Project `.mcp.json`, name `linear`, `Authorization: Bearer ${LINEAR_API_KEY}` | Yes | Yes | Yes, through an environment variable or network secret | One key per workspace to create and store, and actions are attributed to the key's user |
| claude.ai connector | No, one per account | No | Yes | Not Project-bound |

## Recommended Project setup

1. Project setup writes a committed `.mcp.json` to the Project root:
   ```json
   {
     "mcpServers": {
       "linear": {
         "type": "http",
         "url": "https://mcp.linear.app/mcp",
         "headers": { "Authorization": "Bearer ${LINEAR_API_KEY}" }
       }
     }
   }
   ```
   It shares the plugin's endpoint, so it suppresses the official plugin's server in that Project. Keep the plugin as the dependency for Projects that haven't migrated, or drop it. Both work.
2. Create a Linear personal API key inside the Project's workspace. Supply it per Project in one of these ways:
   - Locally: a gitignored file loaded into the shell, such as `direnv` with `.envrc`. Or a `headersHelper` that reads the key from the macOS keychain under a per-Project item, which keeps the key out of the shell environment. **[unverified]** We have not checked whether `env` in `.claude/settings.local.json` feeds `.mcp.json` expansion. Test it before relying on it.
   - In the cloud: one cloud environment per Project, with `LINEAR_API_KEY` as an environment variable (or a network secret on Pro or Max), and `remote.defaultEnvironmentId` in the Project's `.claude/settings.json`.
3. Change skills and docs to call the tools through the stable server name `linear`, as `mcp__linear__*`, instead of `mcp__plugin_linear_linear__*`. That includes `docs/agents/issue-tracker.md`.
4. Record this as an amendment to ADR-0001's MCP consequence, or as a new ADR. The Linear MCP becomes a per-Project `.mcp.json` written by setup, and is no longer a plugin dependency.

If interactive OAuth (no key to manage) matters more than cloud support, use OAuth with the name `linear` and a per-Project marker header. Verify first that sign-ins really stay separate across two Projects.

## Open checks (cheap to run)

- Does `${LINEAR_API_KEY}` from `.claude/settings.local.json` `env` expand in `.mcp.json`?
- Does mcp.linear.app accept a personal API key as `Bearer`, and does it ignore an extra `X-Project` header?
- Do two OAuth definitions that differ only by a header get separate keychain entries? Check the `mcpOAuth` keys after signing in from two Projects.
- Does a cloud network secret for `mcp.linear.app` reach MCP traffic from `.mcp.json`?

## Sources

- Linear MCP docs: https://linear.app/docs/mcp
- Linear OAuth 2.0: https://linear.app/developers/oauth-2-0-authentication
- Linear GraphQL / API keys: https://linear.app/developers/graphql
- Claude Code MCP: https://code.claude.com/docs/en/mcp
- Claude Code cloud sessions: https://code.claude.com/docs/en/claude-code-on-the-web
- Claude Code cloud environments: https://code.claude.com/docs/en/cloud-environments
- Official `linear` plugin: anthropics/claude-plugins-official `external_plugins/linear/.mcp.json` and `.claude-plugin/plugin.json` (local marketplace clone)
- Secondary: https://docs.sim.ai/integrations/linear-service-account (API key workspace scoping)
