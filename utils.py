from tornado.web import URLSpec

import csv
import urllib.request
import codecs


def unpack(first, *rest):
    return first, rest


def include(prefix, module_path):
    module = __import__(module_path, globals(), locals(), fromlist=["*"])
    urls = getattr(module, 'urls')
    print(urls)
    final_urls = list()
    for url in urls:
        pattern = url.regex.pattern
        if pattern.startswith("/"):
            pattern = r"%s%s" % (prefix, pattern[1:])
        else:
            pattern = r"%s%s" % (prefix, pattern)
        final_urls.append(URLSpec(pattern, url.handler_class, kwargs=url.kwargs, name=url.name))
    return final_urls


def request_stock(url, stock_code):
    ftpstream = urllib.request.urlopen(url.replace('STOCK_CODE', stock_code))
    csvfile = csv.reader(codecs.iterdecode(ftpstream, 'utf-8'))
    return build_message(csvfile)


def build_message(csvfile):
    next(csvfile)
    line = next(csvfile)
    text = '{} quote is ${} per share'.format(line[0], line[6]) if line[6] != 'N/D' else 'Not recognized stock code'
    return text


def build_leaving_message(user, routing_key, n_users):
    return {
        'name': user,
        'stage': 'stop',
        'msg_type': routing_key,
        'msg': user + ' left',
        'participants': n_users - 1
    }


def get_stock_code(text):
    return text.split('=')[1]


def get_destinate(text):
    return text.split('=')[0]
