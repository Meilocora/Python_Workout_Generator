def to_bool(input_string):
    if input_string == "True":
        return True
    else:
        return False


def transform_attributes(attribute):
    return str(attribute).replace("_", " ").title()


def spruce_up_exercises(exercises):
    for exercise in exercises:
        exercise.type = transform_attributes(exercise.type)
        exercise.equipment = transform_attributes(exercise.equipment)
    return exercises


def transform_workout_exercises(ex):
    return ex.replace('\'', '').replace('[', '').replace(']', '').strip().split('|')[0]


def add_to_exercise_string(ex_string, ex):
    try:
        new_string = ex_string[:-1] + ex + "]"
    except TypeError:
        return f"['{ex}']"
    else:
        return new_string
