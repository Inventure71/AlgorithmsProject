def merge_by_key(left, right, key, reverse=False):
    """
    Merges two sorted lists into one sorted list based on a key function

    - Time: Worst case = Average case = O(n + m) where n and m are lengths of left and right lists
    - Space: O(n + m) for the result list
    """
    result, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        left_val, right_val = key(left[i]), key(right[j])
        # flip comparison if reverse=True
        if (left_val <= right_val) != reverse:
            result.append(left[i]); i += 1
        else:
            result.append(right[j]); j += 1
    return result + left[i:] + right[j:]

def merge_sort_by_key(items, key, reverse=False):
    """
    Merge sort implementation with custom key function

    - Time: Worst case = Average case = O(n log n) divides list in half recursively log n levels and merges at each level with n work
    - Space: O(n) for temporary arrays during merge plus O(log n) recursion stack
    """
    if len(items) <= 1:
        return items
    mid = len(items) // 2
    left = merge_sort_by_key(items[:mid], key, reverse)
    right = merge_sort_by_key(items[mid:], key, reverse)
    return merge_by_key(left, right, key, reverse)

def sort_for_visualization(unique_troops, ascending_order=True):
    """
    Sorts troops by vertical position for proper rendering order

    - Time: Worst case = Average case = O(n log n) due to merge sort
    - Space: O(n) for list conversion plus merge sort temporary arrays
    """
    return merge_sort_by_key(
        list(unique_troops),
        key=lambda t: t.location[0],
        reverse=not ascending_order
    )