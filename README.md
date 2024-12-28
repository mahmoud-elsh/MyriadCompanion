# Myriad Companion
A Destiny 2 companion application utilizing the Bungie API.

## Features
- Transfer items between characters.

- Transfer items from vault and back.

- Equip items from inventory.

- View statistics from all gamemodes.

## Installation
To run the project on your local machine:

### Step 1: Clone the Repository
```
git clone https://github.com/mahmoud-elsh/MyriadCompanion.git
cd MyriadCompanion
```
### Step 2: Setup Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```
### Step 3: Install Dependencies
```
pip install -r requirements.txt
```
### Step 4: Register Bungie Application
Register for an application from https://www.bungie.net/en/Application

### Step 5: Run manifest.py
```
python manifest.py
```
*You can either download the manifest.pickle file or run the manifest.py to download Destiny 2's gameworld database and convert it into a Python dictionary.*

### Step 6: Run the Main Application
```
python main.py
```
- Get the API key, OAuth client_id, and OAuth client_secret from the application and input into program.

- Open the link given by the program and log into your Destiny 2 account.

- You will be redirected back to this page, input the URL into the program to continue.
