from myriadCompanion import *

user = myriadCompanion()
user.setMembershipId()
user.setCharacter()
while True:
    print("Welcome to MyriadCompanion!")
    print("Please select what you would like to do!")
    print("1) Transfer items between characters")
    print("2) Transfer items from vault")
    print("3) Equip Items")
    print("4) View Statistics")
    print("5) Exit")

    selection = int(input())
    if selection == 5:
        print("Thank you!")
        break
    while selection < 1 or selection > 4:
        selection = int(input("Select a valid choice."))

    if selection == 1:
        user.transfer()
    elif selection == 2:
        user.vault()
    elif selection == 3:
        user.equipItem()
    elif selection == 4:
        user.viewStats()
