def write_to_file(data: list, file_path: str) -> None:
    import csv
    if not data:
        return

    keys = data[0].keys()
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def output_to_file(result, file_name):
    output_path = 'output/kraken/'
    import os
    os.makedirs(output_path, 0o777, True)
    try:
        os.chmod('output', 0o777)
        os.chmod(output_path, 0o777)
    except:
        pass

    write_to_file(result, output_path + file_name)
    try:
        os.chmod(output_path + file_name, 0o666)
    except:
        pass
