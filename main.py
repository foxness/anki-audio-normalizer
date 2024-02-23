# -----
# Anki Audio Normalizer 0.0.1
# -
# Created on 2024/02/23 by Haonoke
# -----

# ----- REQUIREMENTS -----
#
# - ffmpeg installed on your system
#

# ----- INSTRUCTIONS -----
# 
# 1. Back up your Anki decks
# 2. Copy the collection.media folder from Anki to somewhere else ("the input folder")
# 3. Run this script on the input folder (adjust config as needed)
# 4. Copy the contents of the output folder into the input folder, replacing all the files (the output folder only has changed audio)
# 5. Replace Anki's collection.media folder with the input folder
# 6. We're done. Run Anki.
#

import os
import subprocess
from pathlib import Path

# ----- CONFIG START -----

INPUT_DIR = '/your/path/to/inputdir'
EXTENSIONS = ['.mp3', '.ogg', '.webm', '.wav']

OUTPUT_DIR = '/your/path/to/outputdir'

# Filters to apply
TRIM_SILENCE = True
NORMALIZE_LEVELS = True

SHOW_FFMPEG_OUTPUT = False

# ----- CONFIG END -----

def main():
    if Path(OUTPUT_DIR).exists():
        print(f'Output folder already exists ({OUTPUT_DIR})')
        return
    
    files = get_files(INPUT_DIR, EXTENSIONS)
    print_filecount(files)
    
    output_files = process_files(files, OUTPUT_DIR)

def get_files(dir, extensions):
    all_files = [os.path.join(dir, f) for f in os.listdir(dir)]
    all_files = [f for f in all_files if os.path.isfile(f)]
    
    extensions = [a.lower() for a in extensions]
    filtered_files = [f for f in all_files if os.path.splitext(f)[-1].lower() in extensions]
    
    return filtered_files

def print_filecount(files):
    extensions = {}
    for file in files:
        filename, file_extension = os.path.splitext(file)
        if file_extension not in extensions:
            extensions[file_extension] = 0
        extensions[file_extension] += 1
    
    for extension, count in sorted(extensions.items(), key=lambda item: -item[1]):
        print(f'{extension}: {count} files')
    
    print(f'\nTotal files: {len(files)}')

def process_files(files, output_dir):
    Path(output_dir).mkdir(parents=True, exist_ok=False)
    print(f'Normalizing...')
    
    output_filepaths = []
    for i, input_filepath in enumerate(files):
        filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(output_dir, filename)
        output_filepaths.append(output_filepath)
        
        normalize_file(input_filepath, output_filepath)
        
        if (i + 1) % 100 == 0:
            print(f'Processed {i + 1} files')
    
    print(f'Normalizing done')
    return output_filepaths

def normalize_file(input_file, output_file):
    audio_filter = get_audio_filter()
    process_args = [
        'ffmpeg',
        '-i', input_file,
        '-filter_complex', audio_filter,
        output_file
    ]
    
    stdout = None
    stderr = None
    if not SHOW_FFMPEG_OUTPUT:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL
    
    subprocess.run(process_args, stdout=stdout, stderr=stderr)

def get_audio_filter():
    # Silence trimming filter
    # ffmpeg -i input_file -af silenceremove=1:0:-50dB output_file
    trimming_filter = 'silenceremove=1:0:-50dB'
    
    # Level normalizing filter
    # ffmpeg -f concat -safe 0 -i list_file -af loudnorm=I=-16:LRA=11:TP=-1.5:print_format=summary -f null -
    # normalizing_filter = 'loudnorm=I=-16:LRA=11:TP=-1.5:print_format=summary'
    normalizing_filter = 'loudnorm=I=-16:LRA=11:TP=-1.5'
    
    audio_filters = []
    if TRIM_SILENCE:
        audio_filters.append(trimming_filter)
    
    if NORMALIZE_LEVELS:
        audio_filters.append(normalizing_filter)
    
    if not audio_filters:
        print('You set all filters to false. I\'m ignoring you lol')
        audio_filters = [trimming_filter, normalizing_filter]
    
    return ','.join(audio_filters)

main()
