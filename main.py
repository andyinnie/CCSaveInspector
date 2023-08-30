# text-based app

from models import Save
from util import pretty_dict

# TODO: WHERE ARE THESE FIELDS?
# settings

while True:
    raw_save = input('Paste save code: ')
    save = Save(raw_save)

    print('Save string in all its raw, decoded glory:')
    print(save.encode())
    print()

    print('Parsed save data:')
    print(pretty_dict(save))
    print()
