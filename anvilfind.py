#!/usr/bin/env python
import nbt
import sys
import argparse
import os


class Rect:
    def __init__(self, s):
        """
        Constructor

        :param s: string in this format: 'xmin,xmax,zmin,zmax'.
        :return: Rectangle
        """
        keys = s.split(',')
        if len(keys) is not 4:
            print('Incorrect rectangle format. Hint: -r="xmin,xmax,zmin,zmax"')
            sys.exit(1)

        self.xmin = int(keys[0])
        self.xmax = int(keys[1])
        self.zmin = int(keys[2])
        self.zmax = int(keys[3])

        # Swap the coordinates if the user isn't able to read the help
        if self.xmin > self.xmax:
            self.xmin, self.xmax = self.xmax, self.xmin
        if self.zmin > self.zmax:
            self.zmin, self.zmax = self.zmax, self.zmin

    def inside(self, x, z):
        """
        Checks if the position is inside the rectangle

        :param x: X coordinate
        :param z: Z coordinate
        :return:
        """
        if x >= self.xmin and x <= self.xmax and z >= self.zmin and z <= self.zmax:
            return True
        return False


def get_block_pos(i, cx, cy, cz):
    """
    Returns absolute position of the block

    :param i: Block number in the chunk
    :param cx: Chunk X coordinate
    :param cy: Chunk Y coordinate
    :param cz: Chunk Z coordinate
    :return: Absolute position of the block
    """
    x = cx*16 + i % 16
    y = cy*16 + int(i/256)
    z = cz*16 + int(i/16) % 16

    return x, y, z


def main(path, id, rect=None):
    """
    The main entry point

    :param path: path to the world
    :param id: block ID
    :param rect: bounding rectangle
    :return: 0
    """
    world = nbt.world.WorldFolder(path)

    positions = list()

    columns_total = 0
    column_count = 0

    # Count columns
    for column in world.iter_nbt():
        cx = column['Level']['xPos'].value
        cz = column['Level']['zPos'].value

        if rect is not None and not rect.inside(cx, cz):
            continue

        columns_total += 1
        sys.stdout.write('{} columns total\r'.format(columns_total))
        sys.stdout.flush()

    print('')  # Jump to the new line

    # Iterate over columns and look for the block
    for column in world.iter_nbt():
        cx = column['Level']['xPos'].value
        cz = column['Level']['zPos'].value

        if rect is not None and not rect.inside(cx, cz):
            continue

        column_count += 1

        sys.stdout.write('Processing column {} of {}\r'.format(column_count, columns_total))
        sys.stdout.flush()

        # Column is divided into 16 chunks
        for chunk in column['Level']['Sections']:
            cy = chunk['Y'].value
            i = 0
            for block_id in chunk['Blocks']:
                x, y, z = get_block_pos(i, cx, cy, cz)

                if block_id == id:
                    positions.append((x, y, z))

                i += 1

    print('')  # Jump to the new line again

    for p in positions:
        print('Block #{} found at {}, {}, {}'.format(id, p[0], p[1], p[2]))

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('path', type=str, help='Path to the world')
    parser.add_argument('ID', type=int, help='Block ID')
    parser.add_argument('-r', '--rect', help='Look for blocks in specified rectangle only. ' +
                                             'Format: -r="xmin,xmax,zmin,zmax"')

    args = parser.parse_args()

    region_path = os.path.join(args.path, 'region')
    if not os.path.exists(region_path):
        print('"{}" doesn\'t look like a world'.format(args.path))
        sys.exit(1)

    if args.rect is None:
        rect = None
    else:
        rect = Rect(args.rect)

    sys.exit(main(args.path, args.ID, rect))
