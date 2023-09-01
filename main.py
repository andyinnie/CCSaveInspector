# text-based app

from models import Save
from util import pretty_dict

while True:
    raw_save = input('Paste save code: ')
    save = Save(raw_save)

    print('Save string in all its raw, decoded glory:')
    print(save.encode())
    print()

    # brocken, idk if i want to bother fixing... i kinda don't care about this cli app
    # print('Parsed save data:')
    # print(pretty_dict(save))
    # print()
