

def linear_search(list, target):
    for index, item in enumerate(list):
        if item == target:
            return index

    return -1