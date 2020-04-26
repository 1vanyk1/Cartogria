def date_more(date1, date2):  # дата1 > дата2
    if date1[0] > date2[0]:
        return True
    if date1[0] == date2[0]:
        if date1[1] > date2[1]:
            return True
        if date1[1] == date2[1]:
            if date1[2] > date2[2]:
                return True
    return False


def date_less(date1, date2):  # дата1 < дата2
    if date1[0] < date2[0]:
        return True
    if date1[0] == date2[0]:
        if date1[1] < date2[1]:
            return True
        if date1[1] == date2[1]:
            if date1[2] < date2[2]:
                return True
    return False


def date_more_or_equal(date1, date2):  # дата1 >= дата2
    if date1[0] > date2[0]:
        return True
    if date1[0] == date2[0]:
        if date1[1] > date2[1]:
            return True
        if date1[1] == date2[1]:
            if date1[2] >= date2[2]:
                return True
    return False


def date_less_or_equal(date1, date2):  # дата1 <= дата2
    if date1[0] < date2[0]:
        return True
    if date1[0] == date2[0]:
        if date1[1] < date2[1]:
            return True
        if date1[1] == date2[1]:
            if date1[2] <= date2[2]:
                return True
    return False


def date_equal(date1, date2):  # дата1 == дата2
    if date1[0] == date2[0]:
        if date1[1] == date2[1]:
            if date1[2] == date2[2]:
                return True
    return False


def date_not_equal(date1, date2):  # дата1 != дата2
    if date1[0] != date2[0]:
        if date1[1] != date2[1]:
            if date1[2] != date2[2]:
                return True
    return False