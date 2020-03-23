def get_param(function, int_diff, initial_params, index_to_insert, initial_value, score):
    current_max = 1
    current_min = 0
    value = initial_value
    print(str(function).split()[1], value, end="")
    actual_score = int_diff.check_approx(function, initial_params[:index_to_insert]
                                         + (value,) + initial_params[index_to_insert:])[0]
    print("", str(actual_score))
    while abs(score - actual_score) > (score / 1000):
        print(str(function).split()[1], end="")
        if actual_score > score:
            current_min = value
            print("", 1, end="")
        elif actual_score < score:
            current_max = value
            print("", -1, end="")
        print("", current_min, current_max, end="")
        print("", (current_max + current_min) / 2, end="")
        new_score = int_diff.check_approx(function, initial_params[:index_to_insert]
                                          + (value := abs((current_max + current_min) / 2),)
                                          + initial_params[index_to_insert:])[0]
        if new_score == actual_score:
            return value
        actual_score = new_score
        print("", str(actual_score))
    return value
