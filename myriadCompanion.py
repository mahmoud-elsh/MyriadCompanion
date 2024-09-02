import json
from requests_oauthlib import OAuth2Session
from tkinter import *
import pickle


def convertInt(hash):
    id = int(hash)
    if (id & (1 << (32 - 1))) != 0:
        id = id - (1 << 32)
    return id


class myriadCompanion:
    API_KEY = ""
    CLIENT_ID = ""
    CLIENT_SECRET = ""

    redirect_url = "https://mahmoud-elsh.github.io/MyriadCompanion/"
    base_auth_url = "https://www.bungie.net/en/OAuth/Authorize"
    token_url = "https://www.bungie.net/platform/app/oauth/token/"

    def __init__(self):
        try:
            with open('manifest.pickle', 'rb') as data:
                self.manifest = pickle.load(data)
        except FileNotFoundError:
            print("Manifest not found! Run manifest.py to download locally.")
            return

        self.inputGUI()

        self.session = OAuth2Session(client_id=self.CLIENT_ID, redirect_uri=self.redirect_url)
        auth_link = self.session.authorization_url(self.base_auth_url)
        print(f"Authorization link: {auth_link[0]}")
        self.redirect_response = input("Paste url link here: ")

        self.session.fetch_token(
            client_id=self.CLIENT_ID,
            client_secret=self.CLIENT_SECRET,
            token_url=self.token_url,
            authorization_response=self.redirect_response
        )
        self.additional_headers = {'X-API-Key': self.API_KEY}

        self.characters = []

        whitelist = {"Xbox": 1, "Psn": 2, "Steam": 3, "Stadia": 5}
        print("Please select your platform: ")
        for words in whitelist.keys():
            print(words)
        selection = input()
        selection = selection.capitalize()

        if selection not in whitelist:
            selection = input("Please input a correct platform: ")
            selection = selection.capitalize()

        self.membershipType = whitelist[selection]

    def inputGUI(self):
        def getInfo():
            self.API_KEY = input1.get()
            self.CLIENT_ID = input2.get()
            self.CLIENT_SECRET = input3.get()
            root.destroy()

        root = Tk()
        root.title("Enter Credentials")
        root.geometry("200x200")
        apikey_label = Label(root, text="API Key:")
        apikey_label.pack()
        input1 = Entry(root)
        input1.pack()

        clientid_label = Label(root, text="Client ID:")
        clientid_label.pack()
        input2 = Entry(root)
        input2.pack()

        client_secret_label = Label(root, text="Client Secret:")
        client_secret_label.pack()
        input3 = Entry(root)
        input3.pack()

        submit_label = Button(root, text="Submit", command=getInfo)
        submit_label.pack(pady=20)

        root.mainloop()

    def setMembershipId(self):
        user_details_endpoint = "https://www.bungie.net/Platform/User/GetMembershipsForCurrentUser/"
        response = self.session.get(url=user_details_endpoint, headers=self.additional_headers)
        temp = response.json()
        self.membershipId = temp["Response"]["primaryMembershipId"]

    def setCharacter(self):
        characters_endpoint = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{self.membershipId}/?components=200"
        response = self.session.get(url=characters_endpoint, headers=self.additional_headers)
        temp = response.json()
        self.characterIds = list(temp["Response"]["characters"]["data"].keys())
        for i in range(len(self.characterIds)):
            self.characters.append(temp["Response"]["characters"]["data"][self.characterIds[i]])

    def transfer(self):
        if self.characterList() == -1:
            return
        print(f"{len(self.characters) + 1}) Vault")
        selectionFrom = int(input("Select what character to transfer from:"))
        while selectionFrom > len(self.characters) or selectionFrom < 1:
            selectionFrom = int(input("Please enter a valid character number."))
        selectionTo = int(input("Select where to transfer to:"))
        while selectionTo > len(self.characters) + 1 or selectionTo < 1:
            selectionTo = int(input("Please enter a valid character/vault number."))

        itemListCurrentlyEquipped = self.getCurrentlyEquipped(selectionFrom)
        itemListInventory = self.getInventory(selectionFrom, len(itemListCurrentlyEquipped))

        itemList = itemListCurrentlyEquipped + itemListInventory

        itemNumber = int(input("Choose what item to transfer: "))
        while itemNumber > len(itemList) or itemNumber < 1:
            itemNumber = int(input("Choose a valid number: "))

        if itemNumber < len(itemListCurrentlyEquipped):
            self.equipItemForTransfer(itemListInventory, selectionFrom, itemListCurrentlyEquipped, itemNumber)

        payload = {"itemReferenceHash": itemList[itemNumber - 1]["itemHash"],
                   "stackSize": 1,
                   "transferToVault": True,
                   "itemID": itemList[itemNumber - 1]["itemInstanceId"],
                   "characterId": self.characterIds[selectionFrom - 1],
                   "membershipType": 3}
        payload = json.dumps(payload)

        transfer_url = "https://www.bungie.net/Platform/Destiny2/Actions/Items/TransferItem/"
        response = self.session.post(url=transfer_url, data=payload, headers=self.additional_headers)
        response = response.json()

        if selectionTo == 4:
            if response["ErrorStatus"] == "Success":
                print("Item transferred!")
            else:
                print(f"{response['ErrorStatus']} | {response['Message']}")
            return

        payload = {"itemReferenceHash": itemList[itemNumber - 1]["itemHash"],
                   "stackSize": 1,
                   "transferToVault": False,
                   "itemID": itemList[itemNumber - 1]["itemInstanceId"],
                   "characterId": self.characterIds[selectionTo - 1],
                   "membershipType": 3}
        payload = json.dumps(payload)

        response = self.session.post(url=transfer_url, data=payload, headers=self.additional_headers)
        response = response.json()

        if response["ErrorStatus"] == "Success":
            print("Item transferred!")
        else:
            print(f"{response['ErrorStatus']} | {response['Message']}")

    def getInventory(self, selection, lineNumber):
        character_inventory_endpoint = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{self.membershipId}/Character/{self.characterIds[selection - 1]}/?components=201"
        response = self.session.get(url=character_inventory_endpoint, headers=self.additional_headers)
        temp = response.json()

        print("Inventory:")
        blacklist = ["", "Engrams", "Lost Items", "Finishers", "Quests", "Subclass"]
        itemListFrom = []
        for items in temp["Response"]["inventory"]["data"]["items"]:
            itemInfo = self.checkItem(items)
            perkInfo = self.checkPerks(items)
            if itemInfo["type"] in blacklist:
                continue
            print(f"{lineNumber}) {itemInfo['name']} | {itemInfo['type']} {itemInfo['rarity']} | {perkInfo}")
            itemListFrom.append(items)
            lineNumber += 1
        return itemListFrom

    def getCurrentlyEquipped(self, selection):
        character_equipped_endpoint = f"https://www.bungie.net/Platform/Destiny2/{self.membershipType}/Profile/{self.membershipId}/Character/{self.characterIds[selection - 1]}/?components=205"
        response = self.session.get(url=character_equipped_endpoint, headers=self.additional_headers)
        temp = response.json()

        print("Currently Equipped:")
        i = 1
        blacklist = ["Seasonal Artifact", "Emotes", "Finishers", "Clan Banners", "Subclass"]
        itemList = []
        for items in temp["Response"]["equipment"]["data"]["items"]:
            itemInfo = self.checkItem(items)
            perkInfo = self.checkPerks(items)
            if itemInfo["type"] in blacklist:
                continue
            print(f"{i}) {itemInfo['name']} | {itemInfo['type']} {itemInfo['rarity']} | {perkInfo}")
            itemList.append(items)
            i += 1
        return itemList

    def equipItemForTransfer(self, itemListInventory, selectionFrom, itemListEquipped, itemNumber):
        equip_endpoint = "https://www.bungie.net/Platform/Destiny2/Actions/Items/EquipItem/"

        itemInfo = self.checkItem(itemListEquipped[itemNumber - 1])
        if itemInfo["type"] == "Kinetic Weapons":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Kinetic Weapons" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Energy Weapons":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Energy Weapons" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Power Weapons":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Power Weapons" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Helmet":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Helmet" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Gauntlets":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Gauntlets" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Chest Armor":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Chest Armor" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Leg Armor":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Leg Armor" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Class Armor":
            for items in itemListInventory:
                checkItem = self.checkItem(items)
                if checkItem["type"] == "Class Armor" and checkItem["rarity"] != "Exotic Gear":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Ghost":
            for items in itemListInventory:
                if self.checkItem(items)["type"] == "Ghost":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Vehicle":
            for items in itemListInventory:
                if self.checkItem(items)["type"] == "Vehicle":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Ships":
            for items in itemListInventory:
                if self.checkItem(items)["type"] == "Ships":
                    itemToEquip = items
                    break
        if itemInfo["type"] == "Emblems":
            for items in itemListInventory:
                if self.checkItem(items)["type"] == "Emblems":
                    itemToEquip = items
                    break

        payload = {"itemId": itemToEquip["itemInstanceId"],
                   "characterId": self.characterIds[selectionFrom - 1],
                   "membershipType": self.membershipType}

        payload = json.dumps(payload)
        self.session.post(url=equip_endpoint, data=payload, headers=self.additional_headers)

    def equipItem(self):
        equip_endpoint = "https://www.bungie.net/Platform/Destiny2/Actions/Items/EquipItem/"

        if self.characterList() == -1:
            return
        selection = int(input("Select a character to equip an item on: "))
        while selection > len(self.characterIds) or selection < 1:
            selection = int(input("Select a valid character: "))

        itemList = self.getInventory(selection, 1)
        itemSelection = int(input("Choose an item to equip: "))
        while itemSelection > len(itemList) or itemSelection < 1:
            itemSelection = int(input("Select a valid item: "))

        payload = {"itemId": itemList[itemSelection - 1]["itemInstanceId"],
                   "characterId": self.characterIds[selection - 1],
                   "membershipType": self.membershipType}
        payload = json.dumps(payload)
        response = self.session.post(url=equip_endpoint, data=payload, headers=self.additional_headers)
        response = response.json()
        if response["ErrorStatus"] == "Success":
            print("Item equipped!")
        else:
            print(f"{response['ErrorStatus']} | {response['Message']}")

    def characterList(self):
        if len(self.characters) == 0:
            print("No characters found")
            return -1
        for i in range(len(self.characters)):
            print(
                f"{i + 1}) {self.checkClass(self.characters[i])} | Light: {self.characters[i]['light']} | {self.checkGender(self.characters[i])} | {self.checkRace(self.characters[i])}")

    def checkClass(self, character):
        classHash = character["classHash"]
        id = convertInt(classHash)
        return self.manifest["DestinyClassDefinition"][id]["displayProperties"]["name"]

    def checkGender(self, character):
        genderHash = character["genderHash"]
        id = convertInt(genderHash)
        gender = self.manifest["DestinyGenderDefinition"][id]["displayProperties"]["name"]
        if gender == "Body Type 1":
            return "Male"
        else:
            return "Female"

    def checkRace(self, character):
        raceHash = character["raceHash"]
        id = convertInt(raceHash)
        return self.manifest["DestinyRaceDefinition"][id]["displayProperties"]["name"]

    def checkItem(self, item):
        itemInfo = {}

        itemHash = item["itemHash"]
        bucketHash = item["bucketHash"]
        itemId = convertInt(itemHash)
        bucketId = convertInt(bucketHash)

        try:
            summaryItemHash = self.manifest["DestinyInventoryItemDefinition"][itemId]["summaryItemHash"]
            summaryItemId = convertInt(summaryItemHash)
            itemInfo["rarity"] = self.manifest["DestinyInventoryItemDefinition"][summaryItemId]["displayProperties"][
                "name"]
        except KeyError:
            itemInfo["rarity"] = ""

        try:
            itemInfo["type"] = self.manifest["DestinyInventoryBucketDefinition"][bucketId]["displayProperties"]["name"]
        except KeyError:
            itemInfo["type"] = ""

        itemInfo["name"] = self.manifest["DestinyInventoryItemDefinition"][itemId]["displayProperties"]["name"]

        return itemInfo

    def checkPerks(self, item):
        weapon = self.checkItem(item)
        whitelist = ["Kinetic Weapons", "Power Weapons", "Energy Weapons"]
        if weapon["type"] not in whitelist:
            return ""
        itemInstanceId = item["itemInstanceId"]
        getitem_endpoint = f"https://www.bungie.net/Platform/Destiny2/3/Profile/{self.membershipId}/Item/{itemInstanceId}/?components=302"
        response = self.session.get(url=getitem_endpoint, headers=self.additional_headers)
        temp = response.json()
        perks_list = ""
        for perks in temp["Response"]["perks"]["data"]["perks"]:
            perkHash = perks["perkHash"]
            id = convertInt(perkHash)
            perk = self.manifest["DestinySandboxPerkDefinition"][id]["displayProperties"]["name"]
            if perk == "":
                continue
            perks_list += perk
            perks_list += " | "
        return perks_list

    def viewStats(self):
        if self.characterList() == -1:
            return
        selection = int(input("Select what character to view stats for:"))
        while selection > 3 or selection < 1:
            selection = int(input("Please enter a valid character number."))

        stats_endpoint = f"https://www.bungie.net/Platform/Destiny2/3/Account/{self.membershipId}/Character/{self.characterIds[selection - 1]}/Stats/"
        response = self.session.get(url=stats_endpoint, headers=self.additional_headers)
        temp = response.json()

        whitelist = ["allPvP", "patrol", "raid", "story", "allStrikes", "allPvE"]
        print("Which stats would you like to view?")
        for words in whitelist:
            print(words)
        selection = input()

        while selection not in whitelist:
            selection = input("Please enter a valid stat: ")

        for key, val in temp["Response"][selection]["allTime"].items():
            print(f"{val['statId']} = {val['basic']['displayValue']}")

    def vault(self):
        vault_endpoint = f"https://www.bungie.net/Platform/Destiny2/{self.membershipType}/Profile/{self.membershipId}/?components=102"

        if self.characterList() == -1:
            return

        selectionTo = int(input("Select where to transfer to:"))
        while selectionTo > len(self.characters) + 1 or selectionTo < 1:
            selectionTo = int(input("Please enter a valid character number."))

        response = self.session.get(url=vault_endpoint, headers=self.additional_headers)
        temp = response.json()

        blacklist = ["", "Engrams", "Lost Items", "Finishers", "Quests", "Subclass", "Modifications", "Consumables"]
        i = 1
        itemList = []
        for items in temp["Response"]["profileInventory"]["data"]["items"]:
            itemInfo = self.checkItem(items)
            perkInfo = self.checkPerks(items)
            if itemInfo["type"] in blacklist:
                continue
            print(f"{i}) {itemInfo['name']} | {itemInfo['type']} | {perkInfo}")
            itemList.append(items)
            i += 1

        itemNumber = int(input("Select an item to transfer"))
        while itemNumber > len(itemList) or itemNumber < 1:
            itemNumber = int(input("Select a valid item."))

        payload = {"itemReferenceHash": itemList[itemNumber - 1]["itemHash"],
                   "stackSize": 1,
                   "transferToVault": False,
                   "itemID": itemList[itemNumber - 1]["itemInstanceId"],
                   "characterId": self.characterIds[selectionTo - 1],
                   "membershipType": 3}
        payload = json.dumps(payload)

        transfer_url = "https://www.bungie.net/Platform/Destiny2/Actions/Items/TransferItem/"
        response = self.session.post(url=transfer_url, data=payload, headers=self.additional_headers)
        response = response.json()

        if response["ErrorStatus"] == "Success":
            print("Item transferred!")
        else:
            print(f"{response['ErrorStatus']} | {response['Message']}")
