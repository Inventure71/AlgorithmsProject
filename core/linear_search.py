


def linear_search(list, target):
    """
    Performs a linear scan over a list to find the target element

    - Time: Worst case = Average case = O(n) where n is the length of the list, iterates through each element once
    - Space: O(1) only uses constant extra space for index variable

    TODO: explain why we use this and not alternative: Binary Search would be O(log n) but requires sorted data; our list is unsorted so Linear Search is optimal for unsorted collections
    """
    for index, item in enumerate(list):
        if item == target:
            return index

    return -1