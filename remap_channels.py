import argparse
import json
import os
import shutil
import urllib.request

# This is something that needs to be configured by you
# CHANNEL_ID --> CHANNEL_NUMBER (must be int in string)
transformations = [
    "TVP 1 HD",
    "TVP 2 HD",
    "TVP 3 Warszawa",
    "Polsat",
    "TVN HD",
    "TVN",
    "TV 4",
    "TV Puls",
    "TVN 7 HD",
    "TVN 7",
    "TV Puls 2",
    "TV6",
    "Super Polsat",
    "ESKA TV",
    "TTV HD",
    "TTV",
    "Polo TV",
    "ATM Rozrywka",
    "TV Trwam",
    "Stopklatka TV",
    "Fokus TV",
    "TVP ABC",
    "TVP Kultura",
    "TVP Historia",
    "TVP Sport",
    "TVP Info",
]


def download(url, file_name):
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(file_name, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    print(f"Downloaded {url} as {file_name}")


def fix_channel_name(channel_name):
    """ For now, removes only spaces"""
    return channel_name.replace(" ", "")


def generate_channel_map(channel_list):
    """
        This function fixes all the channels on the list.
    """
    channel_map = {}
    for channel in channel_list:
        channel_map[channel] = fix_channel_name(channel_name=channel)

    return channel_map


def patch_channel_map(channel_map, forced_channel_map=None, prefix="0"):
    """
        For the generated channel map, adds forced identifiers 
    """
    forced_channel_map = forced_channel_map or {}

    patched_channel_map = {}
    for channel_initial_name, channel_target_name in channel_map.items():
        patched_channel_name = channel_target_name

        if channel_initial_name in forced_channel_map.keys():
            forced_channel_id = forced_channel_map.get(channel_initial_name, "")
            patched_channel_name = f"{prefix}{forced_channel_id}{patched_channel_name}"

        patched_channel_map[channel_initial_name] = patched_channel_name

    return patched_channel_map


def rename_remap(file_in, file_out, forced_channel_map=None):
    forced_channel_map = forced_channel_map or {}
    with open(file_in, "rt") as fin:
        with open(file_out, "wt") as fout:
            for line in fin:
                # Pass just the keys of forced_channel_map for now (in the end, should pass all the channels from xml)
                channel_map = generate_channel_map(
                    channel_list=forced_channel_map.keys()
                )
                # Force channel numbers
                channel_map = patch_channel_map(
                    channel_map=channel_map, forced_channel_map=forced_channel_map
                )

                # Try to fix lines with all the possible fixes, iterate over channel_map
                fixed_line = line
                for channel_name, fixed_channel_name in channel_map.items():
                    fixed_line = fixed_line.replace(
                        f'="{channel_name}"', f'="{fixed_channel_name}"'
                    )

                fout.write(fixed_line)

    print(f"Remapped {file_in} to {file_out}")


def upload(filename, target_path):
    destination_filename = os.path.join(target_path, filename)
    shutil.copyfile(filename, destination_filename)

    print(f"Uploaded {filename} to {destination_filename}")


if __name__ == "__main__":
    """ 
    Usage example: 
        python remap_channels.py https://URL/guide.xml epg.xml epg-fixed.xml /network/tvdir/
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="source of the XML EPG")
    parser.add_argument("epg_file_name", help="desired downloaded file name")
    parser.add_argument(
        "epgfixed_file_name", help="desired target name of the XML file"
    )
    parser.add_argument("target_path", help="place on the server")
    args = parser.parse_args()

    download(url=args.url, file_name=args.epg_file_name)
    forced_channel_map = {}
    with open('map.json', 'r') as forced_channel_json:
        forced_channel_map = json.load(forced_channel_json)

    rename_remap(
        file_in=args.epg_file_name,
        file_out=args.epgfixed_file_name,
        forced_channel_map=forced_channel_map,
    )
    upload(filename=args.epgfixed_file_name, target_path=args.target_path)
