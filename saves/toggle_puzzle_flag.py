"""Set a bool flag (HasBeenSolved / HasBeenOpened) for a given puzzle path in a .sav file.

Usage:
    python3 toggle_puzzle_flag.py <in.sav> <out.sav> <puzzle_path> <true|false> [flag_name]

flag_name defaults to HasBeenSolved.

Examples:
    python3 toggle_puzzle_flag.py SaveFile1.sav SaveFile1.sav AGeri/Puzzles/Data/Tutorial-1 false
    python3 toggle_puzzle_flag.py SaveFile1.sav SaveFile1.sav AGeri/Puzzles/Data/Tutorial-1 true HasBeenOpened
"""
import sys
import struct


def fstr(s):
    b = s.encode('ascii') + b'\x00'
    return struct.pack('<i', len(b)) + b


def set_flag(data, puzzle_path, value: bool, flag_name: str):
    tag = fstr('PuzzleID') + fstr('StrProperty')
    flag_tag = fstr(flag_name) + fstr('BoolProperty')
    key_marker = fstr(puzzle_path)

    idx = data.find(key_marker + tag)
    if idx == -1:
        return data, False

    search_region = data[idx:idx + 4000]
    sm = search_region.find(flag_tag)
    if sm == -1:
        return data, False

    off = idx + sm + len(flag_tag)
    boolval_pos = off + 8

    data = bytearray(data)
    changed = data[boolval_pos] != (1 if value else 0)
    data[boolval_pos] = 1 if value else 0
    return bytes(data), changed


if __name__ == '__main__':
    if len(sys.argv) not in (5, 6):
        print(__doc__)
        sys.exit(1)

    src, dst, puzzle_path, value_str = sys.argv[1:5]
    flag_name = sys.argv[5] if len(sys.argv) == 6 else 'HasBeenSolved'
    value = value_str.strip().lower() == 'true'

    data = open(src, 'rb').read()
    new_data, changed = set_flag(data, puzzle_path, value, flag_name)

    if not changed and new_data == data:
        found = data.find(fstr(puzzle_path)) != -1
        print(f"puzzle path {'found but already at target value' if found else 'NOT FOUND'}: {puzzle_path}")
        if not found:
            sys.exit(1)

    open(dst, 'wb').write(new_data)
    print(f"wrote {dst}: {puzzle_path} {flag_name}={value} (changed={changed})")
