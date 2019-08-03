import argparse
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


def rename_remap(file_in, file_out):
    with open(file_in, "rt") as fin:
        with open(file_out, "wt") as fout:
            for line in fin:
                fixed_line = line
                range_size = len(transformations)
                for i in range(range_size):
                    channel_name = transformations[i]
                    # What to FIX?
                    input_string = f'="{channel_name}"'
                    # Add numbering
                    output_number = i + 1
                    output_string = f'="0{output_number}{channel_name}"'
                    # Remove spaces
                    output_string = output_string.replace(" ", "")

                    fixed_line = fixed_line.replace(input_string, output_string)

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

    # print(args.url)
    # print(args.epg_file_name)
    # print(args.epgfixed_file_name)
    # print(args.target_path)

    download(url=args.url, file_name=args.epg_file_name)
    rename_remap(file_in=args.epg_file_name, file_out=args.epgfixed_file_name)
    upload(filename=args.epgfixed_file_name, target_path=args.target_path)
