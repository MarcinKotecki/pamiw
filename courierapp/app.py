import requests
import re
import os
from tabulate import tabulate as tab
from dotenv import load_dotenv

load_dotenv()
WEBSERVICE_URL = os.environ.get('WEBSERVICE_URL_COURIER')
AUTH0_LOCAL_URL = os.environ.get('AUTH0_LOCAL_URL')
AUTH0_TOKEN = os.environ.get('AUTH0_TOKEN')
AUTH0_HEADER = {"Authorization": f"Bearer {AUTH0_TOKEN}"}

VALID_STATUSES = ['label_created', 'preparing_package', 'package_sent', 'package_delivered', 'package_received']

def get_auth_token():
    r = requests.get(AUTH0_LOCAL_URL, headers=AUTH0_HEADER)
    if r.status_code == 200:
        return {"Authorization": f"Bearer {r.json()['message']}"}
    else:
        return {"Authorization": f"Bearer 0"}

def get_packages():
    r = requests.get(f"{WEBSERVICE_URL}/package", headers=get_auth_token())
    if r.status_code == 200:
        return r.json()['packages']
    else:
        return False

def change_package_status(id, status):
    r = requests.patch(f"{WEBSERVICE_URL}/package/{id}", json={"status":status}, headers=get_auth_token())
    if r.status_code == 200:
        return "success"
    elif r.status_code == 404:
        return "invalid id"
    else:
        return "Couldn't update status"


def pprint(array):
    print(tab(array[::-1], headers='keys', tablefmt='fancy_grid'))

print('---------------------------------------------------------------')
print("-Welcome to Courierapp. TYPE 'help' to list availible commands-")
print('---------------------------------------------------------------')
running = True
while(running):
    x = input('> ')
    if re.compile(f'help.*').match(x):
        print('Availible commands:')
        print('\thelp                               -- prints help')
        print('\tpackages                           -- prints list of all packages')
        print("\tpackage set status {uuid} {status} -- updates package's status")
        print('Valid package statuses:')
        print(f"\t{VALID_STATUSES}")
    elif re.compile(f'packages').match(x):
        packages = get_packages()
        if packages:
            pprint(packages)
        else:
            print("Couldn't download packages")
    elif re.compile(f'package set status .+ .+').match(x):
        package_id = x.split(' ')[3]
        package_status = x.split(' ')[4]
        if package_status not in VALID_STATUSES:
            print('Invalid status. Availible options are:')
            print(VALID_STATUSES)
        else:
            print(change_package_status(package_id, package_status))
    elif re.compile(f'exit.*').match(x):
        print('Goodbye')
        running = False
    else:
        print('Unknown command, type help to see all availible commands.')
