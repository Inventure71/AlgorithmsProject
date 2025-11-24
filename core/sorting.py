

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

    
    
    