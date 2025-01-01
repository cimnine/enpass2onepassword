# enpass2onepassword

Tool to migrate from Enpass to 1Password.
This tool takes an Enpass JSON export
and imports it via the 1Password SDK.

## Quick-Start

1. Follow the [Preparations](#Preparations) section below.
2. If on Windows: Install [Python](https://www.python.org/downloads/) on your computer
3. Install this tool, by running the following command in a terminal of your choosing: `pip install enpass2onepassword`
4. Run this tool, by running the following command in a terminal of your choosing: `enpass2onepassword`
5. Fill in the information
   - _Sa name_: The name of your 1Password Service Account
   - _Sa token_: The token (aka credential) for the 1Password Service Account.
   - _Op vault_: The name of the empty(!) 1Password Vault.

[py]: https://www.python.org/downloads/

## Preparations

1. Create a [new 1Password Vaul][op-vault].
   - Call the _Vault_ whatever you like, for example `Enpass`.
   - See [the official documentation][op-docs-vault] for further guidance.
2. Create a [1Password Service Account][op-sa].
   - Call the _Service Account_ whatever you like, for example `enpass2onepassword`
   - Use the cog ⚙️ to add the _write permission_ to the _Service Account_
   - See [the official documentation][op-docs-sa] for further guidance.
3. Copy the _Service Account Token_ (and/or save it to 1password). 
4. Export your _Enpass Vault_ as JSON, for example as `export.json`. 
   - The export is unencrypted!
   - Don't forget to delete the file after a successful import!
   - Ensure, that you export the vault to a place that is not synced to another computer
     or that is immediately backed up.
   - A good place would be an SD card or a USB drive with an encrypted filesystem.

[op-vault]: https://my.1password.eu/vaults/new/custom
[op-docs-vault]: https://support.1password.com/create-share-vaults/
[op-sa]: https://my.1password.eu/developer-tools/infrastructure-secrets/serviceaccount/
[op-docs-sa]: https://developer.1password.com/docs/sdks/setup-tutorial

## Usage Overview

```text
$> enpass2onepassword --help
Usage: enpass2onepassword [OPTIONS] ENPASS_JSON_EXPORT

  Adds items from an Enpass JSON export to a 1Password vault through the
  1Password API.

Options:
  -n, --op-sa-name, --sa TEXT     The 1Password service account name. You
                                  chose this when creating the 1Password
                                  service account.  [default:
                                  enpass2onepassword; required]
  -t, --op-sa-token, --token TEXT
                                  The 1Password service account token. This
                                  was created when creating the 1Password
                                  service account.  [required]
  -o, --op-vault, --vault TEXT    The name of the 1Password vault. All Enpass
                                  items will be created in that 1Password
                                  vault. This 1Password vault must be empty!
                                  Also, the service account must have write
                                  permissions to it.  [default: Enpass;
                                  required]
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
  --silent                        By default, this tool will print status
                                  information while importing to 1Password.
                                  Use this flag to disable such reports.
  --help                          Show this message and exit.
```

## Roadmap

- [ ] Improved support for credit card's expiry date, once [#140][gh-op-140] is implemented
- [ ] Support for importing attachments, once [#139][gh-op-139] is implemented
- [ ] Improved support for Secure Notes, once [#141][gh-op-141] is implemented

[gh-op-139]: https://github.com/1Password/onepassword-sdk-python/issues/139
[gh-op-140]: https://github.com/1Password/onepassword-sdk-python/issues/140
[gh-op-141]: https://github.com/1Password/onepassword-sdk-python/issues/141

## Tip: Load Service Account Credentials via 1Password CLI

Add the credentials of your 1Password Service Account to your private 1Password vault like so:

- Vault: Private
- Type: API Credential
- Name: `Service Account Auth Token`
- Username: `enpass2onepassword` (or whatever you chose as username)
- Password: `ops_…` (the secret generated by 1Password)

> Note: If you choose other names, you need to adjust `main.env` for the following to work!

Then [install the 1Password CLI][op-docs-cli] and use the following command to run the migration tool:

[op-docs-cli]: https://developer.1password.com/docs/cli/get-started

```shell
# load the venv
. .venv/bin/activate

# unlock 1Password CLI
op signin

# specify the paths to the secrets
export OP_SERVICE_ACCOUNT_NAME="op://Private/Service Account Auth Token/username"
export OP_SERVICE_ACCOUNT_TOKEN="op://Private/Service Account Auth Token/credential"

# inject the secrets
op run -- enpass2onepassword ~/Desktop/export.json
```

## Tip: List all categories in export

To list all the categories in the Enpass export, use the following command:

```shell
jq '[.items[].category] | unique' export.json
```

## Tip: List all field types in export

To list all the field types in the Enpass export, use the following command:

```shell
jq '[.items[] | select(.fields != null) | .fields[]] | flatten | [.[].type] | unique' export.json
```

## Tip: Split your export by category

To split your export by category, use the following command:

```shell
jq '{folders: .folders, items: [.items[] | select(.category == "uncategorized")]}' export.json > export_uncat.json
#                                                               ^^^^^^^^^^^^^ Change category here
```

## Development

This project uses [poetry][poetry] for dependency management, building and publishing.

Run the development build:

```shell
poetry install
poetry run enpass2onepassword
```

[poetry]: https://python-poetry.org/

## Copyright and License

Copyright © 2025 Christian Mäder.
[See `LICENSE` for license](./LICENSE).
