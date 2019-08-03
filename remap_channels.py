import os

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
    "TVN7 HD",
    "TVN 7",
    "PULS 2",
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
    "TVP Info"
]

def rename():
    file_in = "epg.xml"
    file_out = "epg-fixed.xml"
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
                    output_string = f'="{output_number}{channel_name}"'
                    # Remove spaces
                    output_string = output_string.replace(" ", "")

                    fixed_line = fixed_line.replace(input_string, output_string)

                fout.write(fixed_line)


if __name__ == '__main__':
    rename()
