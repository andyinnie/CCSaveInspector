from datetime import datetime


class Encodable:
    def encode(self) -> str:
        raise NotImplementedError


def fmt(data: any) -> str:
    if issubclass(type(data), Encodable):
        return data.encode()

    if type(data) not in [int, float]:
        return str(data)

    return format(data, '.0f')


def format_time(timestamp: int):
    return (datetime.fromtimestamp(timestamp // 1000)
            .strftime('%Y-%m-%d %I:%M:%S %p %Z'))


def _pretty_dict(dictionary: any, tabs: int = 0) -> str:
    prefix = '\t' * tabs

    if type(dictionary) is not dict:
        if hasattr(dictionary, 'fields'):
            dictionary = dictionary.fields
        else:
            return prefix + str(dictionary)

    lines = []
    for k, v in dictionary.items():
        value = v

        if hasattr(v, 'fields'):
            value = v.fields

        if type(value) is dict:
            lines.append(f'{prefix}{k}:')
            if len(value):
                lines.append(_pretty_dict(value, tabs+1))
        elif type(value) is list:
            lines.append(f'{prefix}{k}:')
            for e in value:
                lines.append(_pretty_dict(e, tabs+1) + ',')
        else:
            lines.append(f'{prefix}{k}: {fmt(value)}')
    return '\n'.join(lines)


# recursively print a dictionary with each line like    key: value
def pretty_dict(obj: any) -> str:
    return _pretty_dict(obj)
