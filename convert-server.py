import re
import nbt
import glob
import requests
import os
import sys
from hashlib import md5

from json.decoder import JSONDecodeError


def get_offline_uuid(username):
    string = "OfflinePlayer:" + username
    hash = md5(string.encode('utf-8')).digest()
    byte_array = [byte for byte in hash]
    byte_array[6] = hash[6] & 0x0f | 0x30
    byte_array[8] = hash[8] & 0x3f | 0x80
    hash_modified = bytes(byte_array)
    uuid = hash_modified.hex()
    uuid_formatted = (
        uuid[:8] + '-' +
        uuid[8:12] + '-' +
        uuid[12:16] + '-' +
        uuid[16:20] + '-' +
        uuid[20:]
    )

    return uuid_formatted


def get_online_uuid(name):
    response = requests.get(url='https://api.mojang.com/users/profiles/minecraft/' + name)

    try:
        data = response.json()
        data_uuid = data['id']

        if len(data_uuid) != 32:
            return data_uuid

        matches = re.match('(\w{8})(\w{4})(\w{4})(\w{4})(\w{12})', data_uuid)
        uuid = "{}-{}-{}-{}-{}".format(matches.group(1), matches.group(2), matches.group(3), matches.group(4), matches.group(5))

        print('Name: ' + name + ' found: ' + uuid)

        return uuid
    
    except JSONDecodeError:
        print('Name: ' + name + ' not found')

        return ""


def get_old_uuids():
    player_dats = glob.glob("world/playerdata/*.dat")

    uuids = []

    for filename in player_dats:
        search = re.match('world/playerdata/(.*)\\.dat', filename)

        uuids.append(search.group(1))

    return uuids


def get_uuids_conversion(uuids, on_to_off=True):
    conversion = []
    get_uuid = get_offline_uuid if on_to_off else get_online_uuid

    for uuid in uuids:
        nbtfile = nbt.nbt.NBTFile('world/playerdata/' + uuid + '.dat', 'rb')
        username = str(nbtfile['bukkit']['lastKnownName'])
        new_uuid = get_uuid(username)
        if new_uuid == "":
            continue

        conversion.append([uuid, new_uuid])

    return conversion


def convert_player(original, new):
    try:
        os.rename('world/playerdata/' + original + '.dat', 'world/playerdata/' + new + '.dat')
        os.chmod('world/playerdata/' + new + '.dat', 0o666)
    except:
        print('File does not exist: ' + 'world/playerdata/' + original + '.dat')
    try:
        os.rename('world/playerdata/' + original + '.dat_old', 'world/playerdata/' + new + '.dat_old')
        os.chmod('world/playerdata/' + new + '.dat_old', 0o666)
    except:
        print('File does not exist: ' + 'world/playerdata/' + original + '.dat_old')


def convert_stats(original, new):
    try:
        os.rename('world/stats/' + original + '.json', 'world/stats/' + new + '.json')
        os.chmod('world/stats/' + new + '.json', 0o666)
    except:
        print('File does not exist: ' + 'world/stats/' + original + '.json')


def convert_advancements(original, new):
    try:
        os.rename('world/advancements/' + original + '.json', 'world/advancements/' + new + '.json')
        os.chmod('world/advancements/' + new + '.json', 0o666)
    except:
        print('File does not exist: ' + 'world/advancements/' + original + '.json')


def convert_files(conversions):
    for conversion in conversions:
        convert_player(conversion[0], conversion[1])
        convert_stats(conversion[0], conversion[1])
        convert_advancements(conversion[0], conversion[1])
        print('Converted ' + conversion[0] + ' -> ' + conversion[1])


if __name__ == "__main__":
    uuids = get_old_uuids()
    uuids_conversion = get_uuids_conversion(uuids, len(sys.argv) == 1)
    convert_files(uuids_conversion)
    print('Done')
