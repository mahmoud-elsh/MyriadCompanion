import requests, zipfile, os, pickle, json, sqlite3


def get_manifest():
    manifest_url = "http://www.bungie.net/Platform/Destiny2/Manifest/"

    response = requests.get(manifest_url)
    manifest = response.json()
    mani_url = "http://www.bungie.net" + manifest['Response']['mobileWorldContentPaths']['en']

    response = requests.get(mani_url)
    with open("MANZIP", "wb") as zip:
        zip.write(response.content)
    print("Download Complete!")

    with zipfile.ZipFile('MANZIP') as zip:
        name = zip.namelist()
        zip.extractall()
    os.rename(name[0], 'Manifest.content')
    print('Unzipped!')


table_names = {
    "DestinyClassDefinition",
    "DestinyGenderDefinition",
    "DestinyInventoryItemDefinition",
    "DestinyRaceDefinition",
    "DestinyInventoryBucketDefinition",
    "DestinySandboxPerkDefinition"
}

manifest = {}


def build_dict(table_names):
    con = sqlite3.connect('manifest.content')
    cur = con.cursor()

    for table_name in table_names:
        query = f"""
        SELECT id, json
        FROM {table_name}
        """

        cur.execute(query)

        data_dict = {}

        rows = cur.fetchall()

        for row in rows:
            id = row[0]  # Assuming the first column is the ID
            json_data = json.loads(row[1])  # Assuming the second column contains JSON as text
            data_dict[id] = json_data
        manifest[table_name] = data_dict
    return manifest


if not os.path.isfile(r'path\to\file\manifest.content'):
    get_manifest()
    all_data = build_dict(table_names)
    with open('manifest.pickle', 'wb') as data:
        pickle.dump(all_data, data)
        print("'manifest.pickle' created!")
else:
    print('Pickle Exists')
