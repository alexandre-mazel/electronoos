import argparse
from pathlib import Path

import numpy as np
import soundfile as sf


TARGET_DBFS = -1.0
TARGET_DBFS = 0.0
NORMALIZATION_TOLERANCE = 0.01


def get_peak_dbfs(audio):
    peak = np.max(np.abs(audio))

    if peak <= 0:
        return float("-inf")

    return 20 * np.log10(peak)


def normalize_audio(audio):
    peak = np.max(np.abs(audio))
    target_peak = 10 ** (TARGET_DBFS / 20)

    if peak <= 0:
        return audio, 0.0

    gain = target_peak / peak

    if abs(gain - 1.0) <= NORMALIZATION_TOLERANCE:
        return audio, 0.0

    return audio * gain, 20 * np.log10(gain)


def process_file(file_path):
    try:
        audio, sample_rate = sf.read( file_path, always_2d=False )
        original_dbfs = get_peak_dbfs( audio )

        normalized_audio, gain_db = normalize_audio( audio )

        if gain_db == 0.0:
            print( f"{file_path.name}: nothing to do" )
            return

        sf.write( file_path, normalized_audio, sample_rate )
        print( f"{file_path.name}: {gain_db:+.2f} dB" )

    except Exception as error:
        print( f"{file_path.name}: error - {error}" )


def main():
    parser = argparse.ArgumentParser( description="Normalize WAV files" )
    parser.add_argument( "path", type=Path, nargs="?", default=Path( "." ) )

    args = parser.parse_args()

    if not args.path.is_dir():
        raise NotADirectoryError( f"Invalid directory: {args.path}" )

    wav_files = sorted( args.path.glob( "*.wav" ) )

    for file_path in wav_files:
        process_file( file_path )


if __name__ == "__main__":
    main( )