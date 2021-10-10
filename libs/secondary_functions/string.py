import re


def chunk_string(string, length):
    """Возвращает string разбитую по словам на части длины не больше length"""

    if len(string) <= length:
        return [string]

    chunked_string = ['']
    for word in string.split(' '):
        if len(word) > length:
            raise ValueError('Length should be more than the longest word!')

        if len(chunked_string[-1] + ' ' + word) <= length:
            chunked_string[-1] += (' ' + word) if chunked_string[-1] != '' else word
        else:
            chunked_string.append(word)
    return chunked_string


def filter_html_tags(string, tags_to_filter):
    template = '|'.join(r'(</?{}.*?>)'.format(tag) for tag in tags_to_filter)
    return re.sub(template, '', string)
