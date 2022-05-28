from typing import List


async def admin_search(admins_list_id: List[int], current_id: int):
    """Binary search for admins"""

    sorted_list = sorted(admins_list_id)

    first = sorted_list.index(sorted_list[0])
    last = len(sorted_list) - 1

    while first <= last:

        mid = (first + last) // 2

        if sorted_list[mid] < current_id:
            first = mid + 1

        elif sorted_list[mid] > current_id:
            last = mid - 1

        else:
            return True

    return False
