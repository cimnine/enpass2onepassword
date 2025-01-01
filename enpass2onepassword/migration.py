import json

import click

from aiostream import stream
from onepassword import ItemCreateParams, ItemCategory, ItemFieldType, ItemSection, Website, AutofillBehavior, ItemField
from onepassword.client import Client


async def migrate(ep_file, op_sa_name, op_sa_token, op_vault, ignore_non_empty, no_confirm, silent):
    try:
        client = await Client.authenticate(auth=op_sa_token, integration_name=op_sa_name, integration_version="v1.0.0")
    except Exception as e:
        click.echo(f"An error occured while setting up the connection to 1Password: {click.style(e, fg='red')}",
                   err=True)
        click.echo("Check the 1Password Service Account name and token, and try again.")
        raise click.Abort()

    vaults = await client.vaults.list_all()

    if not vaults:
        click.echo(message=f"The 1Password Service Account '{op_sa_name}' does not have access to any vaults.",
                   err=True)
        raise click.Abort()

    vault = None
    async for vault in vaults:
        if vault.title == op_vault:
            vault = vault
            break

    if not vault:
        click.echo(
            message=f"The vault '{op_vault}' does not exist or the 1Password Service Account '{op_sa_name}' does not have access.",
            err=True)
        raise click.Abort()
    op_vault_id = vault.id

    # item = await client.items.get(vault_id=op_vault_id, item_id='uuid')
    # breakpoint()

    op_items_async_iter = await client.items.list_all(vault.id)
    op_items = await stream.list(op_items_async_iter)
    if op_items and not ignore_non_empty:
        click.echo(
            message=f"The vault '{op_vault}' already contains items.",
            err=True)
        raise click.Abort()

    enpass = json.load(ep_file)
    if not enpass:
        click.echo(
            message=f"Unable to load the given Enpass export.",
            err=True)
        raise click.Abort()
    ep_items = enpass['items']

    folders_mapping = {}
    for folder in enpass['folders']:
        folders_mapping[folder['uuid']] = folder['title']

    op_items = []
    for ep_item in ep_items:
        category = map_category(ep_item)
        autofill_behavior = AutofillBehavior.NEVER \
            if ep_item['auto_submit'] == 0 \
            else AutofillBehavior.ANYWHEREONWEBSITE

        if category == ItemCategory.PASSWORD:
            websites = ([Website(url=field['value'], label=field['label'], autofill_behavior=autofill_behavior) for
                         field in
                         ep_item['fields'] if field['type'] == 'url' or field['type']]
                        +
                        [Website(url=field['value'], label=field['label'],
                                 autofill_behavior=AutofillBehavior.ANYWHEREONWEBSITE) for field in
                         ep_item['fields'] if field['type'] == 'url' or field['type'] == '.Android#'])
        else:
            websites = None

        sections = map_sections(ep_item)
        fields = map_fields(ep_item)

        note = ep_item.get('note', None)
        if note:
            fields.append(ItemField(
                id='note',
                title='Note',
                field_type=ItemFieldType.TEXT,
                value=note,
                section_id=''
            ))

        op_item = ItemCreateParams(
            title=ep_item['title'],
            vault_id=op_vault_id,
            tags=[folders_mapping[uuid] for uuid in ep_item['folders']] if 'folders' in ep_item else None,
            category=category,
            sections=sections,
            websites=websites,
            fields=fields
        )
        op_items.append(op_item)

    ep_total = len(ep_items)
    op_total = len(op_items)

    if not silent:
        click.echo(f"{click.style(ep_total, fg='green')} Enpass entries have been analyzed.")
        click.echo(f"{click.style(op_total, fg='green')} 1Password entries will be created.")

    if not no_confirm:
        click.echo("Type 'y' to continue: ", nl=False)
        c = click.getchar()
        click.echo()
        if c != 'y':
            raise click.Abort()

    for i, op_item in enumerate(op_items):
        if not silent and i % 10 == 0:
            click.echo(f"Creating entry {i} of {op_total} …")

        await client.items.create(op_item)

    if not silent:
        click.echo(f"{click.style('Done.', fg='green')} Migrated {op_total} entries.")


def map_sections(item):
    default_sections = [ItemSection(id='', title='')]
    fields = item.get('fields', None)
    if not fields:
        return default_sections

    return default_sections + [ItemSection(id=str(field['uid']), title=field['label']) for field in fields
                               if field['type'] == 'section']


def map_fields(item):
    fields = item.get('fields', None)
    if not fields:
        return []

    current_section_uid = ''

    result = []
    for field in sorted(fields, key=lambda f: f['order']):
        if field['deleted'] != 0:
            continue
        if field['type'] == 'section':
            current_section_uid = str(field['uid'])
            continue
        if field['type'] == '.Android#':
            continue

        sensitive = field['sensitive'] != 0

        result.append(ItemField(
            id=str(field['uid']),
            title=field['label'],
            field_type=ItemFieldType.CONCEALED if sensitive else map_field_type(item, field),
            value=field['value'],
            section_id=current_section_uid
        ))

    return result


field_type_map = {
    ".Android#": ItemFieldType.URL,
    "ccBankname": ItemFieldType.TEXT,
    "ccCvc": ItemFieldType.CONCEALED,
    "ccExpiry": ItemFieldType.TEXT,
    "ccName": ItemFieldType.TEXT,
    "ccNumber": ItemFieldType.CREDITCARDNUMBER,
    "ccPin": ItemFieldType.CONCEALED,
    "ccTxnpassword": ItemFieldType.CONCEALED,
    "ccType": ItemFieldType.CREDITCARDTYPE,
    "ccValidfrom": ItemFieldType.TEXT,
    "date": ItemFieldType.TEXT,
    "email": ItemFieldType.TEXT,
    "multiline": ItemFieldType.TEXT,
    "numeric": ItemFieldType.TEXT,
    "password": ItemFieldType.CONCEALED,
    "phone": ItemFieldType.PHONE,
    "pin": ItemFieldType.CONCEALED,
    "section": ItemFieldType.UNSUPPORTED,
    "text": ItemFieldType.TEXT,
    "totp": ItemFieldType.TOTP,
    "url": ItemFieldType.URL,
    "username": ItemFieldType.TEXT,
}


def map_field_type(item, field):
    c = field_type_map.get(field['type'], None)
    if c:
        return c

    click.echo(f"Unexpected field type '{field['type']}' on field '{field['label']}' ({field['uid']}) " +
               f"on item '{item['title']}' ({item['uuid']})", err=True)
    raise click.Abort()


category_map = {
    'computer': ItemCategory.ROUTER,
    'creditcard': ItemCategory.CREDITCARD,
    'finance': ItemCategory.BANKACCOUNT,
    'identity': ItemCategory.IDENTITY,
    'license': ItemCategory.SOFTWARELICENSE,
    'login': ItemCategory.LOGIN,
    'misc': ItemCategory.SECURENOTE,
    'note': ItemCategory.SECURENOTE,
    'password': ItemCategory.PASSWORD,
    'travel': ItemCategory.PASSPORT,
    'uncategorized': ItemCategory.SECURENOTE,
}


def map_category(item):
    c = category_map.get(item['category'], None)
    if c:
        return c

    click.echo(f"Unexpected category '{item['category']}' on item '{item['title']}' ({item['uuid']})", err=True)
    raise click.Abort()
