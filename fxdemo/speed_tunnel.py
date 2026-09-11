import argparse
import math
import cv2
import numpy as np


def draw_glow_line( frame, points, width, intensity = 1.0 ):
    glow = np.zeros_like( frame )
    integer_points = np.asarray( points, dtype = np.int32 ).reshape( -1, 1, 2 )
    cv2.polylines( glow, [ integer_points ], False, ( 255, 255, 255 ), width, cv2.LINE_AA )
    blurred = cv2.GaussianBlur( glow, ( 0, 0 ), width * 2.5 )
    frame[:] = cv2.addWeighted( frame, 1.0, blurred, 0.75 * intensity, 0 )
    frame[:] = cv2.addWeighted( frame, 1.0, glow, intensity, 0 )


def draw_particles( frame, time, particle_count, center_x, center_y ):
    height, width = frame.shape[:2]
    glow = np.zeros_like( frame )

    for index in range( particle_count ):
        seed = index * 12.9898 + 78.233
        phase = seed - math.floor( seed )
        depth = ( phase + time * 0.34 ) % 1.0
        perspective = depth ** 2.15
        radius = 18.0 + perspective * max( width, height ) * 0.78
        angle = index * 2.399963 + depth * 8.0 + math.sin( time * 1.8 + phase * 20.0 ) * 0.12
        angle += math.sin( depth * 5.0 + time * 1.1 ) * 0.16

        x = center_x + math.cos( angle ) * radius
        y = center_y + math.sin( angle ) * radius * 0.86

        previous_depth = max( 0.0, depth - 0.035 )
        previous_radius = 18.0 + previous_depth ** 2.15 * max( width, height ) * 0.78
        previous_angle = index * 2.399963 + previous_depth * 8.0
        previous_x = center_x + math.cos( previous_angle ) * previous_radius
        previous_y = center_y + math.sin( previous_angle ) * previous_radius * 0.86

        if -20 < x < width + 20 and -20 < y < height + 20:
            length = 1.5 + perspective * 13.0
            thickness = max( 1, int( 0.7 + perspective * 2.8 ) )
            brightness = int( 90 + perspective * 165 )
            cv2.line( glow, ( int( previous_x ), int( previous_y ) ),
                      ( int( x ), int( y ) ), ( brightness, brightness, brightness ),
                      thickness, cv2.LINE_AA )

    blurred = cv2.GaussianBlur( glow, ( 0, 0 ), 3.0 )
    frame[:] = cv2.addWeighted( frame, 1.0, blurred, 0.65, 0 )
    frame[:] = cv2.addWeighted( frame, 1.0, glow, 0.9, 0 )


def draw_tunnel( frame, time, center_x, center_y ):
    height, width = frame.shape[:2]
    points = []

    for step in range( 180 ):
        depth = step / 179.0
        radius = 22.0 + depth * max( width, height ) * 0.73
        angle = depth * math.pi * 2.65 + time * 0.55
        x = center_x + math.cos( angle ) * radius
        y = center_y + math.sin( angle ) * radius * 0.86
        points.append( ( x, y ) )

    draw_glow_line( frame, points, 7, 0.85 )

    inner_points = []

    for step in range( 120 ):
        depth = step / 119.0
        radius = 12.0 + depth * max( width, height ) * 0.34
        angle = depth * math.pi * 2.65 + time * 0.55 + 0.18
        x = center_x + math.cos( angle ) * radius
        y = center_y + math.sin( angle ) * radius * 0.86
        inner_points.append( ( x, y ) )

    draw_glow_line( frame, inner_points, 4, 0.75 )


def create_frame( frame_index, fps, width, height, particle_count ):
    time = frame_index / fps
    frame = np.zeros( ( height, width, 3 ), dtype = np.uint8 )

    center_x = width * 0.43 + math.sin( time * 0.55 ) * width * 0.018
    center_y = height * 0.55 + math.cos( time * 0.43 ) * height * 0.012

    draw_particles( frame, time, particle_count, center_x, center_y )
    draw_tunnel( frame, time, center_x, center_y )

    vignette_x = np.linspace( -1.0, 1.0, width )
    vignette_y = np.linspace( -1.0, 1.0, height )
    xx, yy = np.meshgrid( vignette_x, vignette_y )
    vignette = 1.0 - 0.42 * np.clip( ( xx * xx + yy * yy ) ** 0.8, 0.0, 1.0 )
    frame[:] = np.clip( frame.astype( np.float32 ) * vignette[ ..., None ], 0, 255 ).astype( np.uint8 )

    return frame


def main( ):
    parser = argparse.ArgumentParser( description = "Generate a monochrome speed tunnel animation." )
    parser.add_argument( "--output", default = "speed_tunnel.mp4" )
    parser.add_argument( "--width", type = int, default = 540 )
    parser.add_argument( "--height", type = int, default = 540 )
    parser.add_argument( "--fps", type = int, default = 30 )
    parser.add_argument( "--duration", type = float, default = 5.0 )
    parser.add_argument( "--particles", type = int, default = 520 )
    args = parser.parse_args( )
    
    print("Generating...")

    frame_count = int( args.duration * args.fps )
    writer = cv2.VideoWriter(
        args.output,
        cv2.VideoWriter_fourcc( *"mp4v" ),
        args.fps,
        ( args.width, args.height )
    )

    if not writer.isOpened( ):
        raise RuntimeError( "Unable to open the output video." )

    for frame_index in range( frame_count ):
        frame = create_frame(
            frame_index,
            args.fps,
            args.width,
            args.height,
            args.particles
        )
        if 0:
            cv2.imshow("fx",frame)
            cv2.waitKey(10)
        writer.write( frame )

    writer.release( )


if __name__ == "__main__":
    main( )
