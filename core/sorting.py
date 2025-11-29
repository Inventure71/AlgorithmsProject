
def merge_by_key(left, right, key):
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def merge_sort_by_key(items, key):
    if len(items) <= 1: return items
    mid = len(items) // 2
    return merge_by_key(merge_sort_by_key(items[:mid], key), merge_sort_by_key(items[mid:], key), key)

def sort_for_visualization(unique_troops, ascending_order=True):
    # we only want from top to bottom or viceversa we ignore the horizontal position
    unique_troops = list(unique_troops)

    return merge_sort(unique_troops, ascending_order)

def merge(left, right, ascending_order=True):
    result = []

    index_left = 0
    index_right = 0

    # we need to merge and sort the two lists
    while index_left < len(left) and index_right < len(right):
        if (left[index_left].location[0] < right[index_right].location[0] and ascending_order) or (left[index_left].location[0] > right[index_right].location[0] and not ascending_order): 
            result.append(left[index_left])
            index_left += 1
        else:
            result.append(right[index_right])
            index_right += 1

    # we add the remaining elements if we stopped because one list was fully navigated
    result.extend(left[index_left:])
    result.extend(right[index_right:])
    return result
        
def merge_sort(unique_troops, ascending_order=True):

    if len(unique_troops) <= 1:
        return unique_troops

    mid = len(unique_troops) // 2
    left = unique_troops[:mid]
    right = unique_troops[mid:]

    left_sorted = merge_sort(left, ascending_order)
    right_sorted = merge_sort(right, ascending_order)
    return merge(left_sorted, right_sorted, ascending_order)

    
    
    