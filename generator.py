import random
import numpy as np

from utils import to_bool
from workout_boundaries import TYPES, EQUIPMENT


def generate_workout(form, all_exercises):
    stations = form.stations.data
    min_difficulty = form.min_difficulty.data
    max_difficulty = form.max_difficulty.data
    equipment_required = to_bool(form.equipment_required.data)
    fav_only = to_bool(form.fav_only.data)
    partner_workout = to_bool(form.partner_workout.data)
    dont_repeat = to_bool(form.dont_repeat.data)

    feasible_exercises = filter_feasible_exercises(min_difficulty, max_difficulty, equipment_required, fav_only, partner_workout, all_exercises)

    return build_workout(stations, dont_repeat, feasible_exercises)


def filter_feasible_exercises(min_difficulty, max_difficulty, equipment_required, fav_only, partner_workout, all_exercises):

    feasible_exercises = [exercise for exercise in all_exercises if
                          min_difficulty <= exercise.difficulty <= max_difficulty]

    if not equipment_required:
        feasible_exercises = [exercise for exercise in feasible_exercises if exercise.equipment == "none"]
    if fav_only:
        feasible_exercises = [exercise for exercise in feasible_exercises if exercise.favourite]
    if partner_workout:
        feasible_exercises = [exercise for exercise in feasible_exercises if exercise.partner_required]
    else:
        feasible_exercises = [exercise for exercise in feasible_exercises if not exercise.partner_required]

    return feasible_exercises


def build_workout(stations, dont_repeat, feasible_exercises):
    available_equipment = [equipment[0] for equipment in EQUIPMENT]
    training_types = [training_type[0] for training_type in TYPES]
    random.shuffle(training_types)

    exercises_by_types = {}
    for training_type in training_types:
        exercises_by_types[training_type] = [ex for ex in feasible_exercises if ex.type == training_type]

    workout = []

    if dont_repeat:
        if not enough_exercises(stations, exercises_by_types):
            return False

    counter = 0
    ex_counter = 0
    difficulties = []
    while ex_counter < stations:
        if counter >= len(training_types):
            counter = 0
        # Randomly get an exercise from the available exercises of the type
        try:
            random_exercise = random.choice(exercises_by_types[training_types[counter]])
        except IndexError:
            return False

        if dont_repeat:
            # Remove from the available exercises, so they don't repeat
            exercises_by_types[training_types[counter]].remove(random_exercise)
            counter += 1

        if random_exercise.equipment != "none" and random_exercise.equipment not in available_equipment:
            # When equipment is needed but not available anymore -> skip exercise
            continue
        elif random_exercise.equipment != "none" and random_exercise.equipment in available_equipment:
            available_equipment.remove(random_exercise.equipment)
        workout.append(f"{random_exercise.id}|{random_exercise.name}")
        ex_counter += 1
        difficulties.append(random_exercise.difficulty)

    # Calculate difficulty
    difficulty = round(np.mean(difficulties))

    # Calculate required equipment
    required_equipment = [eq for eq in [equipment[0] for equipment in EQUIPMENT] if eq not in available_equipment]
    if len(required_equipment) == 0:
        required_equipment = "none"
    else:
        required_equipment = ', '.join(required_equipment)

    workout_details = []
    workout_details.extend([str(workout), difficulty, required_equipment])
    return workout_details


def enough_exercises(stations, exercises_by_types):
    available_equipment = [equipment[0] for equipment in EQUIPMENT]
    training_types = [training_type[0] for training_type in TYPES]

    stations_per_type = stations / len(training_types)

    for ex_type in exercises_by_types:
        num_of_exercises = 0
        for ex in exercises_by_types[ex_type]:
            if ex.equipment != 'none' and ex.equipment not in available_equipment:
                continue
            elif ex.equipment != 'none' and ex.equipment in available_equipment:
                available_equipment.remove(ex.equipment)
            num_of_exercises += 1
        if num_of_exercises < stations_per_type:
            return False
    return True
