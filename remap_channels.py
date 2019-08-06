import argparse
import json
import ftplib
import os
import shutil
import urllib.request

# Using "".format() to make it compatibile with python pre 3.7 as it is going to be used
# on RPis and other older machines


def download(url, file_name):
    # Download the file from `url` and save it locally under `file_name`:
    with urllib.request.urlopen(url) as response, open(file_name, "wb") as out_file:
        shutil.copyfileobj(response, out_file)

    print(
        "Downloaded {url} as {file_name}".format(**{"url": url, "file_name": file_name})
    )


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


def patch_channel_map(channel_map, forced_channel_map=None):
    """
        For the generated channel map, adds forced identifiers 
    """
    forced_channel_map = forced_channel_map or {}

    patched_channel_map = {}
    for channel_initial_name, channel_target_name in channel_map.items():
        patched_channel_name = channel_target_name

        if channel_initial_name in forced_channel_map.keys():
            forced_channel_id = forced_channel_map[channel_initial_name]
            patched_channel_name = "{forced_channel_id}".format(
                **{"forced_channel_id": forced_channel_id}
            )

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
                        '="{channel_name}"'.format(**{"channel_name": channel_name}),
                        '="{fixed_channel_name}"'.format(
                            **{"fixed_channel_name": fixed_channel_name}
                        ),
                    )

                fout.write(fixed_line)

    print(
        "Remapped {file_in} to {file_out}".format(
            **{"file_in": file_in, "file_out": file_out}
        )
    )


def upload(filename, target_path):
    """
        Obsolete
    """
    destination_filename = os.path.join(target_path, filename)
    shutil.copyfile(filename, destination_filename)

    print(
        "Uploaded {filename} to {destination_filename}".format(
            **{"filename": filename, "destination_filename": destination_filename}
        )
    )


def upload_ftp(
    filename, ftp_address, username, password, destination_dir, destination_filename
):
    with ftplib.FTP(ftp_address) as ftp:
        ftp.login(username, password)
        ftp.cwd(destination_dir)
        ftp.dir()

        with open(filename, "rb") as fp:
            cmd = "STOR {destination_filename}".format(
                **{"destination_filename": destination_filename}
            )
            ftp.storbinary(cmd, fp)

        ftp.dir()
        ftp.close()

    print(
        "Uploaded {filename} to FTP: {ftp_address}/{destination_dir}/{destination_filename}".format(
            **{
                "filename": filename,
                "ftp_address": ftp_address,
                "destination_dir": destination_dir,
                "destination_filename": destination_filename,
            }
        )
    )


if __name__ == "__main__":
    """ 
    Usage example: 
        python remap_channels.py config.json
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("config_filename", help="config JSON file name")
    args = parser.parse_args()

    with open(args.config_filename, "r") as config_json:
        config = json.load(config_json)

        epg = config["epg"]
        shared_resource = config.get("shared_resource")
        ftp_creds = config.get("ftp")

        download(url=epg["source"], file_name=epg["local_filename"])

        rename_remap(
            file_in=epg["local_filename"],
            file_out=epg["fixed_local_filename"],
            forced_channel_map=config["channels"],
        )

        if shared_resource is not None:
            upload(
                filename=shared_resource["destination_filename"],
                target_path=shared_resource["destination_dir"],
            )

        if ftp_creds is not None:
            upload_ftp(
                filename=epg["fixed_local_filename"],
                ftp_address=ftp_creds["address"],
                username=ftp_creds["username"],
                password=ftp_creds["password"],
                destination_dir=ftp_creds["destination_dir"],
                destination_filename=ftp_creds["destination_filename"],
            )
