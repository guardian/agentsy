# Contributing a plugin

To share a Copilot plugin for your stream, team, guild or other group:

1. The plugin must belong to a GitHub team.  If no suitable team exists, please create one but do this sparingly.  Don't create a team just to manage a plugin!
2. Add the plugin under [`plugins/`](plugins/) in this repository 
   with a `plugin.json` manifest at the root of its directory.  
   See [GitHub's plugin authoring and testing guide](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/plugins-creating) and the [feature-files plugin](plugins/editorial-tools-modernisation.feature-files/) for an example.
   Keep secrets out of the plugin, including its examples and fixtures. 
   Review what it can access and run, and give it only the permissions it needs.
   Try it on a representative task and describe in the pull request what it helped with and how you verified the result.
   More guidance on evaluating plugins is coming soon.
   **The name of the plugin must follow the pattern: `<github-team>.<team-plugin-name>`.**
3. Register the plugin in the [marketplace manifest](.github/plugin/marketplace.json).  
   Add an entry to `plugins` with its name, description, version and a source of `./plugins/<github-team>.<team-plugin-name>`:

   ```text
    {
      "name": "owning-team.great-plugin",
      "description": "An extraordinarily useful plugin.",
      "version": "1.0.0",
      "source": "./plugins/owning-team.great-plugin"
    }, 
   ```

4. Add the owning GitHub team to [`CODEOWNERS`](CODEOWNERS):  

   ```text
   /plugins/owning-team.great-plugin/ @guardian/owning-team
   ```

5. Request a review from the owning team when you open the pull request.
6. Merge after the owning team has approved the plugin and the @guardian/devx-ai-and-automation team has approved
   the marketplace entry and general structure and configuration.
