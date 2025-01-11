from test.helper_ep import enpass

from onepassword import (
    AutofillBehavior,
    ItemCategory,
    ItemCreateParams,
    ItemField,
    ItemFieldType,
    ItemSection,
    Website,
)

from enpass2onepassword.migration import map_fields, map_items


async def test_load():
    ep_folders, ep_items = await enpass("test_email.json")

    assert len(ep_items) == 1
    assert ep_items[0]["category"] == "login"


async def test_note():
    ep_folders, ep_items = await enpass("test_email.json")

    items = await map_items(ep_folders, ep_items, "test")
    assert len(items) == 1

    item = items[0]
    assert item.category == ItemCategory.LOGIN
    assert item.notes == ep_items[0]["note"]

    fields = item.fields
    assert len(fields) == 6
    email_fields = [
        field for field in fields if field.field_type == ItemFieldType.EMAIL
    ]
    assert len(email_fields) == 1
    assert email_fields[0].section_id is None
