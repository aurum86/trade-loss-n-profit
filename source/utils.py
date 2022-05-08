def unique(list1) -> list:
    output = set()
    for x in list1:
        output.add(x)
    return list(output)
