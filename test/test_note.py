from test.helper_ep import enpass

from onepassword import ItemCategory

from enpass2onepassword.migration import map_items


async def test_load():
    ep_folders, ep_items = await enpass("test_note.json")

    assert len(ep_items) == 3
    assert ep_items[0]["category"] == "note"
    assert ep_items[1]["category"] == "note"
    assert ep_items[2]["category"] == "note"


async def test_note():
    ep_folders, ep_items = await enpass("test_note.json")

    items = await map_items(ep_folders, ep_items, "test")
    assert len(items) == 1

    item = items[0]
    assert item.category == ItemCategory.SECURENOTE
    assert item.notes == ep_items[0]["note"]
    assert not item.fields
