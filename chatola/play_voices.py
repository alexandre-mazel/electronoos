import os
import sys
import time
import pygame


def get_wav_files (directory):
    files = []

    for filename in os.listdir (directory):
        if filename.lower ( ).endswith ( ".wav" ):
            files.append ( filename )

    return sorted ( files )


def get_timestamp (filename):
    return filename[:18]


def get_identity (filename):
    name = filename.lower ( )

    if "cpu" in name:
        return "computer"

    if "voice" in name:
        return "human"

    return "unknown"


def get_timestamp_seconds (timestamp):
    try:
        hour = int ( timestamp[9:11] )
        minute = int ( timestamp[11:13] )
        second = int ( timestamp[13:15] )
        millisecond = int ( timestamp[16:19] )

        return hour * 3600 + minute * 60 + second + millisecond / 1000.0

    except ( ValueError, IndexError ):
        return 0


def format_timestamp (timestamp):
    try:
        hour = timestamp[9:11]
        minute = timestamp[11:13]
        second = timestamp[13:15]
        millisecond = timestamp[16:19]

        return "%s:%s:%s.%s" % ( hour, minute, second, millisecond )

    except ( ValueError, IndexError ):
        return timestamp


def draw_identity ( screen, identity, filename, font, small_font ):
    screen.fill ( ( 25, 25, 25 ) )

    width, height = screen.get_size ( )

    if identity == "computer":
        color = ( 70, 150, 255 )

        pygame.draw.rect (
            screen,
            color,
            ( width // 2 - 150, height // 2 - 100, 300, 200 ),
            border_radius = 20
        )

        pygame.draw.rect (
            screen,
            ( 20, 20, 20 ),
            ( width // 2 - 115, height // 2 - 65, 230, 130 ),
            border_radius = 8
        )

        pygame.draw.rect (
            screen,
            color,
            ( width // 2 - 70, height // 2 + 115, 140, 15 ),
            border_radius = 5
        )

        label = "COMPUTER"

    elif identity == "human":
        color = ( 80, 220, 130 )

        pygame.draw.circle (
            screen,
            color,
            ( width // 2, height // 2 - 65 ),
            65
        )

        pygame.draw.ellipse (
            screen,
            color,
            ( width // 2 - 115, height // 2 + 5, 230, 190 )
        )

        label = "HUMAN"

    else:
        color = ( 180, 180, 180 )
        label = "UNKNOWN"

    text = font.render ( label, True, color )
    text_rect = text.get_rect ( center = ( width // 2, 80 ) )
    screen.blit ( text, text_rect )

    filename_text = small_font.render (
        filename,
        True,
        ( 220, 220, 220 )
    )

    filename_rect = filename_text.get_rect (
        center = ( width // 2, height - 45 )
    )

    screen.blit ( filename_text, filename_rect )

    pygame.display.flip ( )


def play_file ( screen, filepath, filename, font, small_font ):
    identity = get_identity ( filename )
    timestamp = get_timestamp ( filename )

    draw_identity (
        screen,
        identity,
        filename,
        font,
        small_font
    )

    print ( "%s  %s  %s" % (
        format_timestamp ( timestamp ),
        identity,
        filename
    ) )

    pygame.mixer.music.load ( filepath )
    pygame.mixer.music.play ( )

    while pygame.mixer.music.get_busy ( ):
        for event in pygame.event.get ( ):
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

        time.sleep ( 0.01 )

    return True


def main ( ):
    if len ( sys.argv ) > 1:
        directory = sys.argv[1]
    else:
        directory = "."

    if not os.path.isdir ( directory ):
        print ( "Directory not found: %s" % directory )
        return 1

    files = get_wav_files ( directory )

    if not files:
        print ( "No WAV files found in: %s" % directory )
        return 0

    pygame.init ( )
    pygame.mixer.init ( )

    screen = pygame.display.set_mode ( ( 800, 600 ) )
    pygame.display.set_caption ( "Voice recordings" )

    font = pygame.font.SysFont ( "DejaVu Sans", 64, bold = True )
    small_font = pygame.font.SysFont ( "DejaVu Sans", 22 )

    try:
        for filename in files:
            filepath = os.path.join ( directory, filename )

            if not play_file (
                screen,
                filepath,
                filename,
                font,
                small_font
            ):
                break

    finally:
        pygame.mixer.music.stop ( )
        pygame.quit ( )

    return 0


if __name__ == "__main__":
    sys.exit ( main ( ) )
