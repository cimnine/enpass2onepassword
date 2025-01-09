from test.helper_ep import enpass


async def test_load():
    ep_folders, ep_items = await enpass("test_note.json")

    assert len(ep_items) >= 1
    assert ep_items[0]["category"] == "note"
