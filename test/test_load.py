from test.helper_ep import enpass

from enpass2onepassword.migration import map_items


async def test_load():
    ep_folders, ep_items = await enpass("test_note.json")

    assert len(ep_folders) == 2
    assert len(ep_items) == 3
    assert ep_items[0]["archived"] == True
    assert ep_items[1]["trashed"] == True
    assert ep_items[2]["archived"] == False
    assert ep_items[2]["trashed"] == False


async def test_skip():
    ep_folders, ep_items = await enpass("test_note.json")

    items = await map_items(ep_folders, ep_items, "test")
    assert len(items) == 1
