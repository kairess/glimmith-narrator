import sys, struct

def find_map_tag(data, prop_name):
    marker = struct.pack('<i', len(prop_name)+1) + prop_name.encode('ascii') + b'\x00' \
             + struct.pack('<i', 12) + b'MapProperty\x00'
    idx = data.find(marker)
    if idx == -1:
        raise ValueError(f"{prop_name} MapProperty tag not found")
    return idx, idx + len(marker)

def read_map_header(data, after_maptype_pos):
    size_pos = after_maptype_pos
    size_val = struct.unpack_from('<q', data, size_pos)[0]
    pos = size_pos + 8
    # KeyType FString
    klen = struct.unpack_from('<i', data, pos)[0]
    pos += 4 + klen
    # ValueType FString
    vlen = struct.unpack_from('<i', data, pos)[0]
    pos += 4 + vlen
    # HasGuid byte
    pos += 1
    payload_start = pos
    num_to_remove = struct.unpack_from('<i', data, payload_start)[0]
    num_entries = struct.unpack_from('<i', data, payload_start+4)[0]
    payload_end = payload_start + size_val
    return {
        'size_pos': size_pos, 'size_val': size_val,
        'payload_start': payload_start, 'num_entries_pos': payload_start+4,
        'num_entries': num_entries, 'payload_end': payload_end,
    }

def fstr(s):
    b = s.encode('ascii') + b'\x00'
    return struct.pack('<i', len(b)) + b

def build_entry(path, version=1):
    key = fstr(path)
    out = bytearray()
    out += key
    # PuzzleID: StrProperty
    out += fstr('PuzzleID')
    out += fstr('StrProperty')
    val = fstr(path)
    out += struct.pack('<q', len(val)) + b'\x00' + val
    # PuzzleVersion: IntProperty
    out += fstr('PuzzleVersion')
    out += fstr('IntProperty')
    out += struct.pack('<q', 4) + b'\x00' + struct.pack('<i', version)
    # HasBeenSolved: BoolProperty (value byte inline, Size=0)
    out += fstr('HasBeenSolved')
    out += fstr('BoolProperty')
    out += struct.pack('<i', 0) + struct.pack('<i', 0) + bytes([1]) + b'\x00'
    # HasBeenOpened: BoolProperty
    out += fstr('HasBeenOpened')
    out += fstr('BoolProperty')
    out += struct.pack('<i', 0) + struct.pack('<i', 0) + bytes([1]) + b'\x00'
    # CellColors: ArrayProperty<IntProperty> empty
    out += fstr('CellColors')
    out += fstr('ArrayProperty')
    out += struct.pack('<q', 4) + fstr('IntProperty') + b'\x00' + struct.pack('<i', 0)
    # StableComponentIDs: ArrayProperty<IntProperty> empty
    out += fstr('StableComponentIDs')
    out += fstr('ArrayProperty')
    out += struct.pack('<q', 4) + fstr('IntProperty') + b'\x00' + struct.pack('<i', 0)
    # EdgeStates: ArrayProperty<EnumProperty> empty
    out += fstr('EdgeStates')
    out += fstr('ArrayProperty')
    out += struct.pack('<q', 4) + fstr('EnumProperty') + b'\x00' + struct.pack('<i', 0)
    # None terminator
    out += fstr('None')
    return bytes(out)

def flip_solved(data, path):
    """Flip HasBeenSolved bool byte to 1 for an existing entry. Returns modified data."""
    tag = fstr('PuzzleID') + fstr('StrProperty')
    solved_tag = fstr('HasBeenSolved') + fstr('BoolProperty')
    path_bytes = path.encode('ascii') + b'\x00'
    len_prefix = struct.pack('<i', len(path_bytes))
    key_marker = len_prefix + path_bytes
    idx = data.find(key_marker + tag)
    if idx == -1:
        return data, False
    search_region = data[idx:idx+4000]
    sm = search_region.find(solved_tag)
    if sm == -1:
        return data, False
    off = idx + sm + len(solved_tag)
    boolval_pos = off + 8
    data = bytearray(data)
    changed = data[boolval_pos] != 1
    data[boolval_pos] = 1
    # also flip HasBeenOpened just in case
    opened_tag = b'HasBeenOpened\x00\r\x00\x00\x00BoolProperty\x00'
    om = search_region.find(opened_tag)
    if om != -1:
        oo = idx + om + len(opened_tag)
        data[oo+8] = 1
    return bytes(data), changed

def add_entries_and_flip(path_in, path_out, existing_paths_to_solve, new_paths_to_add):
    data = open(path_in, 'rb').read()

    for p in existing_paths_to_solve:
        data, changed = flip_solved(data, p)
        print(f"flip existing solved for {p}: changed={changed}")

    idx, after_maptype = find_map_tag(data, 'PuzzleData')
    hdr = read_map_header(data, after_maptype)
    print('map header:', hdr)

    blob = b''.join(build_entry(p) for p in new_paths_to_add)
    insert_pos = hdr['payload_end']

    new_data = bytearray(data)
    # splice in new entries
    new_data[insert_pos:insert_pos] = blob

    # update size field (int64) at size_pos
    new_size = hdr['size_val'] + len(blob)
    struct.pack_into('<q', new_data, hdr['size_pos'], new_size)

    # update num_entries (int32)
    new_num = hdr['num_entries'] + len(new_paths_to_add)
    struct.pack_into('<i', new_data, hdr['num_entries_pos'], new_num)

    open(path_out, 'wb').write(new_data)
    print(f"wrote {path_out}, added {len(new_paths_to_add)} new entries, blob size {len(blob)}")

if __name__ == '__main__' and not (len(sys.argv) > 1 and sys.argv[1] == 'remove'):
    src, dst = sys.argv[1], sys.argv[2]
    existing = sys.argv[3].split(',') if len(sys.argv) > 3 and sys.argv[3] else []
    newp = sys.argv[4].split(',') if len(sys.argv) > 4 and sys.argv[4] else []
    add_entries_and_flip(src, dst, existing, newp)

def remove_entry_at(data, tag_pos):
    """Remove one TMap entry given the position of its 'PuzzleID' StrProperty tag.
    Correctly updates the PuzzleData map's Size and NumEntries header fields."""
    null_pos = tag_pos - 5
    i = null_pos - 1
    while i >= 0 and 32 <= data[i] <= 126:
        i -= 1
    str_start = i + 1
    entry_start = str_start - 4  # include the 4-byte length prefix

    none_marker = struct.pack('<i', 5) + b'None\x00'
    none_idx = data.find(none_marker, tag_pos)
    entry_end = none_idx + len(none_marker)
    removed_len = entry_end - entry_start

    idx, after_maptype = find_map_tag(data, 'PuzzleData')
    hdr = read_map_header(data, after_maptype)

    new_data = bytearray(data)
    del new_data[entry_start:entry_end]

    struct.pack_into('<q', new_data, hdr['size_pos'], hdr['size_val'] - removed_len)
    struct.pack_into('<i', new_data, hdr['num_entries_pos'], hdr['num_entries'] - 1)

    return bytes(new_data), removed_len

if len(sys.argv) > 1 and sys.argv[1] == 'remove':
    src, dst, target_path = sys.argv[2], sys.argv[3], sys.argv[4]
    data = open(src, 'rb').read()
    tag = fstr('PuzzleID') + fstr('StrProperty')
    path_bytes = target_path.encode('ascii') + b'\x00'
    key_marker = struct.pack('<i', len(path_bytes)) + path_bytes
    positions = []
    start = 0
    while True:
        idx = data.find(key_marker + tag, start)
        if idx == -1:
            break
        positions.append(idx + len(key_marker))
        start = idx + 1
    print(f"found {len(positions)} occurrence(s) of {target_path}")
    if len(positions) < 2:
        print("nothing to remove (not a duplicate)")
    else:
        # remove all but the LAST occurrence (keep the most recently added one)
        for pos in sorted(positions[:-1], reverse=True):
            data, removed_len = remove_entry_at(data, pos)
            print(f"removed entry at tag_pos={pos}, {removed_len} bytes")
        open(dst, 'wb').write(data)
        print(f"wrote {dst}")
