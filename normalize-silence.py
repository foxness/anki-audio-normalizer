# -----
# Silence Normalizer 0.0.1
# -
# Created on 2024/03/21 by Haonoke
# -----

import subprocess
from pathlib import Path
import sys

# ----- CONFIG START -----

FFMPEG = '/opt/homebrew/bin/ffmpeg' # 'ffmpeg'
NORMALIZE_LEVELS = True
TRIM_SILENCE = True
ADD_NORMAL_SILENCE = False
SILENCE_DURATION = 0.1

SHOW_FFMPEG_OUTPUT = True

# ----- CONFIG END -----

def main():
    input_file = sys.argv[1]
    if not Path(input_file).is_file():
        print(f'didnt find anything at {input_file}')
        return
    
    process_file(input_file)

def process_file(input_file):
    print(f'Normalizing...')
    
    tmp_file = 'tmp.mp3'
    tmp_file2 = 'tmp2.mp3'
    apply_filters(input_file, tmp_file)
    
    if ADD_NORMAL_SILENCE:
        add_silence(tmp_file, tmp_file2)
    
    if ADD_NORMAL_SILENCE:
        run(['rm', tmp_file])
        run(['mv', tmp_file2, input_file])
    else:
        run(['mv', tmp_file, input_file])
    
    print(f'Normalizing done')

def apply_filters(input_file, output_file):
    audio_filter = get_audio_filter()
    process_args = [
        FFMPEG,
        '-i', input_file,
        '-filter_complex', audio_filter,
        output_file
    ]
    
    run(process_args)

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

def add_silence(input_file, output_file):
    silence_path = 'silence.mp3'
    generate_silence_if_needed(silence_path, SILENCE_DURATION)
    
    # ffmpeg -i "concat:silence.mp3|input.mp3" -c copy output.mp3
    process_args = [
        FFMPEG,
        # '-y', # overwrite
        '-i', f'concat:{silence_path}|{input_file}',
        # '-c', 'copy', # copy audiostreams
        output_file
    ]
    
    run(process_args)

def generate_silence_if_needed(path, duration):
    if Path(path).is_file():
        return
    
    # ffmpeg -filter_complex aevalsrc=0 -t 10 10SecSilence.mp3
    process_args = [
        FFMPEG,
        '-filter_complex', 'aevalsrc=0',
        '-t', str(duration),
        path
    ]
    
    run(process_args)

def run(process_args):
    stdout = None
    stderr = None
    if not SHOW_FFMPEG_OUTPUT:
        stdout = subprocess.DEVNULL
        stderr = subprocess.DEVNULL
    
    subprocess.run(process_args, stdout=stdout, stderr=stderr)

main()
