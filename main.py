# -----
# Anki Audio Normalizer 0.0.1
# -
# Created on 2024/02/23 by Haonoke
# -----

# REQUIREMENTS: ffmpeg installed

import os
import subprocess
from pathlib import Path

# ----- CONFIG START -----

INPUT_DIR = 'test_media'
EXTENSIONS = ['.mp3', '.ogg', '.webm', '.wav']

OUTPUT_DIR = 'test_output'

SHOW_FFMPEG_OUTPUT = True
# TRIM_BEGINNING_SILENCE = True

# ----- CONFIG END -----

def main():
    print('hello world')
    # subprocess.run(['rm', '-rf', 'output']) # todo: remove
    
    if Path(OUTPUT_DIR).exists():
        print(f'Output folder already exists ({OUTPUT_DIR})')
        return
    
    files = get_files(INPUT_DIR, EXTENSIONS)
    # files = files[:4]
    print_filecount(files)
    
    output_files = process_files(files, OUTPUT_DIR)
    normalize_levels(output_files)

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
    
    output_filepaths = []
    for i, input_filepath in enumerate(files):
        filename = os.path.basename(input_filepath)
        output_filepath = os.path.join(output_dir, filename)
        output_filepaths.append(output_filepath)
        
        trim_silence(input_filepath, output_filepath) # todo: just copy if not trim
        
        if (i + 1) % 100 == 0:
            print(f'processed {i + 1} files')
    
    print(f'processing done')
    return output_filepaths

def trim_silence(input_file, output_file):
    # trims beginning silence
    
    # ffmpeg -i input_file -af silenceremove=1:0:-50dB output_file
    process_args = [
        'ffmpeg',
        '-i', input_file,
        '-af', 'silenceremove=1:0:-50dB',
        output_file
    ]
    
    stdout = None
    stderr = None
    if not SHOW_FFMPEG_OUTPUT:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL
    
    subprocess.run(process_args, stdout=stdout, stderr=stderr)

def normalize_levels(files):
    list_content = '\n'.join([f"file '{a}'" for a in files])
    
    list_file_name = 'list_file.txt'
    list_file = open(list_file_name, 'w')
    list_file.write(list_content)
    list_file.close()
    
    # ffmpeg -f concat -safe 0 -i list_file -af loudnorm=I=-16:LRA=11:TP=-1.5:print_format=summary -f null -
    process_args = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', list_file_name,
        '-af', 'loudnorm=I=-16:LRA=11:TP=-1.5:print_format=summary',
        '-f', 'null',
        '-'
    ]
    
    stdout = None
    stderr = None
    if not SHOW_FFMPEG_OUTPUT:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL
    
    print(f'normalizing...')
    subprocess.run(process_args, stdout=stdout, stderr=stderr)
    print(f'normalization done')
    
    subprocess.run(['rm', list_file_name])

main()
