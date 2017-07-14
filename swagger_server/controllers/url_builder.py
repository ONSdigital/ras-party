def build_url(template, config, *args):
    url = template.format(config['scheme'], config['host'], config['port'], *args)
    return url
