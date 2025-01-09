from pathlib import Path

from enpass2onepassword.migration import load_enpass_json


async def enpass(enpass_file):
    json_path = Path(__file__).parent.joinpath(enpass_file)
    with open(json_path, mode="r", encoding="utf-8") as json_file:
        ep_folders, ep_items = await load_enpass_json(json_file)

        return ep_folders, ep_items
