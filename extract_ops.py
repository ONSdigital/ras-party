import yaml


if __name__ == '__main__':

    with open('swagger_server/swagger/swagger.yaml') as ifile:
        swagger = yaml.load(ifile)

    for path, ops in swagger['paths'].items():
        print(path)
        for k, v in ops.items():
            print("\t{} = {}".format(k.upper(), v['operationId']))

    # print(swagger)
