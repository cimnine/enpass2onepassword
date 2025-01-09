# enpass2onepassword

Tool to migrate from Enpass to 1Password.
This tool takes [an Enpass JSON export](https://support.enpass.io/app/import-export/importing_data_from_enpass.htm)
and imports it via the [1Password SDK](https://github.com/1Password/onepassword-sdk-python).

## Requirements

- You need [Python 3][py] installed on your system.
- You need `pip` installed on your system.
- You need to know how to open a _Terminal_ aka _Shell_.
    - On macOS, for example _Terminal.app_.
    - On Windows, for example _PowerShell_.
    - On Linux: You know your way.

[py]: https://www.python.org/downloads/

## Quick-Start

1. Follow the [_Preparations_ section](#preparations) below.
2. [Install `uv`][uv-install].
3. Then, in a terminal of your choosing, run the following command:
   ```shell
   uvx enpass2onepassword ~/Documents/no_backup/enpass_export.json
   ```
4. Fill in the information
    - _Sa name_: The name of your 1Password Service Account
    - _Sa token_: The token (aka credential) for the 1Password Service Account.
    - _Op vault_: The name of the empty(!) 1Password Vault.

[uv-install]: https://docs.astral.sh/uv/getting-started/installation/

## Preparations

1. Create a [new 1Password Vault][op-vault].
    - Call the _Vault_ whatever you like, for example `Enpass`.
    - See [the official documentation][op-docs-vault] for further guidance.
2. Create a [1Password Service Account][op-sa].
    - Call the _Service Account_ whatever you like, for example `enpass2onepassword`
    - Use the cog ⚙️ to add the _write permission_ to the _Service Account_
    - See [the official documentation][op-docs-sa] for further guidance.
3. Copy the _Service Account Token_ (and/or save it to 1Password).
4. Export your _Enpass Vault_ as JSON, for example as `export.json`.
    - ⚠️ The export is unencrypted!
    - Don't forget to delete the file after a successful import!
    - Ensure, that you export the vault to a place that is not synced to another computer
      and which is not backed up automatically.
        - If you use _Time Machine_ on _macOS_, create a folder `no_backup` in your _Documents_.
          Then open the _System Settings_.
          Under _General_ click on _Time Machine_.
          Now click on _Options…_.
          Use the `+`-button to add the folder you just created to the _Exclude from Backups_ list.
    - A good place would also be an SD card or a USB drive with an encrypted filesystem.

[op-vault]: https://my.1password.eu/vaults/new/custom
[op-docs-vault]: https://support.1password.com/create-share-vaults/
[op-sa]: https://my.1password.eu/developer-tools/infrastructure-secrets/serviceaccount/
[op-docs-sa]: https://developer.1password.com/docs/sdks/setup-tutorial

## Usage Overview

```text
Usage: enpass2onepassword [OPTIONS] ENPASS_JSON_EXPORT

  Adds items from an Enpass JSON export to a 1Password vault through the
  1Password API.

Options:
  -n, --op-sa-name, --sa TEXT     The 1Password service account name. You
                                  chose this when creating the 1Password
                                  service account.

                                  Can also be supplied as environment variable
                                  'OP_SERVICE_ACCOUNT_NAME'.  [default:
                                  enpass2onepassword; required]
  -t, --op-sa-token, --token TEXT
                                  The 1Password service account token. It was
                                  shown to you when you created the 1Password
                                  service account.

                                  Can also be supplied as environment variable
                                  'OP_SERVICE_ACCOUNT_TOKEN'.  [required]
  -o, --op-vault, --vault TEXT    The name of the 1Password vault. All Enpass
                                  items will be created in that 1Password
                                  vault. This 1Password vault must be empty!
                                  Also, the service account must have write
                                  permissions to it.

                                  Can also be supplied as environment variable
                                  'OP_VAULT'.  [default: Enpass; required]
  --ignore-non-empty-vault        By default, this tool will stop if it
                                  detects that there are already items in a
                                  vault. Use this flag to ignore this behavior
                                  and continue, even if there are already
                                  items in the given vault. If you use this,
                                  you should definitely make a sound backup of
                                  the vault before the import!
  --no-confirm                    By default, this tool will stop before
                                  importing anything to 1Password, and you
                                  need to confirm the import. Use this flag to
                                  ignore this behavior and import without
                                  further confirmation.
  --no-wakelock                   By default, this tool will prevent the
                                  computer to go to sleep while the import is
                                  running. Use this flag to disable this
                                  behavior.

                                  When this flag is defined, then the computer
                                  might go to sleep and interrupt your import.
                                  The import is usually resumed, when your
                                  computer resumes from sleep. The result is
                                  that you won't make the best use of the
                                  1Password rate limits.
  --silent                        By default, this tool will print status
                                  information while importing to 1Password.
                                  Use this flag to disable such reports.
  --skip INTEGER                  Skip the first number of items. This can be
                                  helpful to recover a failed import.
                                  [default: 0]
  --op-rate-limit-hourly INTEGER  1Password enforces a write request rate
                                  limit per 1Password Service Account. The
                                  hourly rate limit as of 2025-01-01 is 100
                                  requests per hour for private, family and
                                  team accounts and 1'000 requests per hour
                                  for Business accounts.

                                  See https://developer.1password.com/docs/service-accounts/rate-limits/ for more info.  [default: 100]
  --op-rate-limit-daily INTEGER   1Password enforces a write request rate
                                  limit per 1Password Account. The daily limit
                                  as of 2025-01-01 is 1'000 requests per hour
                                  for private and family accounts, 5'000 per
                                  day for Teams accounts and 50'000 requests
                                  per hour for Business accounts.

                                  See https://developer.1password.com/docs/service-accounts/rate-limits/ for more info.  [default: 1000]
  --op-client-validity INTEGER    This tool authenticates with the 1Password
                                  server in order to import entries. This
                                  authentication is only valid for a certain
                                  amount of time. With this parameter, you can
                                  adjust the time after which a this tool re-
                                  authenticates with the 1Password server.

                                  The value is in seconds.  [default: 1800]
  --help                          Show this message and exit.
```

## Tip: Load Service Account Credentials via 1Password CLI

Add the credentials of your 1Password Service Account to your private 1Password vault like so:

- Vault: Private
- Type: API Credential
- Name: `Service Account Auth Token`
- Username: `enpass2onepassword` (or whatever you chose as username)
- Password: `ops_…` (the secret generated by 1Password)

> Note: If you choose other names, you need to adjust the commands below to make it work!

Then [install the 1Password CLI][op-docs-cli] and use the following command to run the migration tool:

[op-docs-cli]: https://developer.1password.com/docs/cli/get-started

```shell
# unlock 1Password CLI
op signin

# specify the paths to the secrets
export OP_VAULT="Enpass"
export OP_SERVICE_ACCOUNT_NAME="$(op read 'op://Private/Service Account Auth Token/username')"
export OP_SERVICE_ACCOUNT_TOKEN="$(op read 'op://Private/Service Account Auth Token/password')"

# inject the secrets
uvx enpass2onepassword ~/Desktop/export.json
```

If that does not work, it may help to replace `Private` with the vault's _UUID_ (which is a value like `johaxupyjfamyo2ivigxs64y8n`) in the above snippet.

## Update

Run the following command to update the tool to the latest version.

```shell
uv tool upgrade enpass2onepassword
```

## Roadmap

- [ ] Improved support for credit card's expiry date, once [#140][gh-op-140] is implemented
- [ ] Support for importing attachments, once [#139][gh-op-139] is implemented
- [x] Improved support for Secure Notes, once [#141][gh-op-141] is implemented
- [ ] Improved support for Wireless Networks, once [#142][gh-op-142] is implemented
- [ ] Support for favorites, once [#143][gh-op-143] is implemented

[gh-op-139]: https://github.com/1Password/onepassword-sdk-python/issues/139
[gh-op-140]: https://github.com/1Password/onepassword-sdk-python/issues/140
[gh-op-141]: https://github.com/1Password/onepassword-sdk-python/issues/141
[gh-op-142]: https://github.com/1Password/onepassword-sdk-python/issues/142
[gh-op-143]: https://github.com/1Password/onepassword-sdk-python/issues/143

## jq tips for developers

These tips require that [`jq`][jq] is installed on your computer.

[jq]: https://jqlang.github.io/jq/

### List all categories in export

To list all the categories in the Enpass export, use the following command:

```shell
jq '[.items[].category] | unique' export.json
```

### List all field types in export

To list all the field types in the Enpass export, use the following command:

```shell
jq '[.items[] | select(.fields != null) | .fields[]] | flatten | [.[].type] | unique' export.json
```

### Split your export by category

To split your export by category, use the following command:

```shell
jq '{folders: .folders, items: [.items[] | select(.category == "uncategorized")]}' export.json > export_uncat.json
#                                                               ^^^^^^^^^^^^^ Change category here
```

### Select all items with a note

```shell
jq '{folders: .folders, items: [.items[] | select(.note != "")]}' enpass_complete.json > export_hasnote.json
```

## Development

This project uses [uv][uv] for dependency management, building and publishing.

Run the development build:

```shell
uv sync
uv run enpass2onepassword
```

Update dependencies:

```shell
uv lock --upgrade
```

[uv]: https://docs.astral.sh/uv/

### Linters

This project uses [MegaLinter](https://megalinter.io/latest/).
To run MegaLinter locally:

```shell
npx mega-linter-runner
```

This requires a valid Docker-compatible container runtime to be available, like [Podman](https://podman.io/).
Also, it required a _Node_ installation with `npm`.

## Release

Release procedure:

1. Edit the version in `pyproject.toml`
2. Commit the change
3. `git push`
4. `git tag 0.1.0`
5. `git push --tags`

The rest is taken care of by the _Release_ GitHub Action.

## Copyright and License

Copyright © 2025 Christian Mäder.
[See `LICENSE` for license](./LICENSE).
