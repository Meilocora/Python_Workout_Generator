import numpy as np
from utils import transform_workout_exercises, add_to_exercise_string


class WorkoutManager:
    def __init__(self, db, Workout, Exercise):
        self.db = db
        self.Workout = Workout
        self.Exercise = Exercise

    def get_exercises(self, workout_id):
        current_workout = self.db.get_or_404(self.Workout, workout_id)

        exercises = []
        if current_workout.exercises != 'None':
            for ex in current_workout.exercises.split(','):
                ex_id = transform_workout_exercises(ex)
                try:
                    exercise = self.db.get_or_404(self.Exercise, ex_id)
                except:
                    exercise = self.Exercise(
                        id=ex_id,
                        name="unknown Exercise",
                        description="This Exercise has been deleted",
                        partner_required=False,
                        favourite=False,
                        difficulty=0,
                        equipment="none"
                    )
                exercises.append(exercise)
        return exercises

    def add_exercise(self, workout_id, exercise_id):
        exercise_to_add = self.db.get_or_404(self.Exercise, exercise_id)
        workout_to_edit = self.db.get_or_404(self.Workout, workout_id)
        ex_to_add = f", '{exercise_to_add.id}|{exercise_to_add.name}'"
        workout_to_edit.exercises = add_to_exercise_string(workout_to_edit.exercises, ex_to_add)
        self.db.session.commit()
        self.calculate_details(workout_id)

    def drop_exercise(self, workout_id, exercise_id):
        workout_to_edit = self.db.get_or_404(self.Workout, workout_id)
        exercises = self.get_exercises(workout_id)
        new_exercises = []
        for ex in exercises:
            if int(ex.id) != int(exercise_id):
                new_exercises.append(f"{ex.id}|{ex.name}")
        workout_to_edit.exercises = str(new_exercises)
        self.db.session.commit()
        self.calculate_details(workout_id)

    def calculate_details(self, workout_id):
        workout_to_edit = self.db.get_or_404(self.Workout, workout_id)
        exercises = self.get_exercises(workout_id)
        equipment = ', '.join([ex.equipment for ex in exercises if ex.equipment != "none"])
        if equipment == "":
            equipment = "none"
        difficulty = round(np.mean([ex.difficulty for ex in exercises]))

        workout_to_edit.stations = len(exercises)
        workout_to_edit.equipment = equipment
        workout_to_edit.difficulty = difficulty
        self.db.session.commit()

    def switch_workout_exercises(self, workout_id, exercise_id, direction):
        workout_to_edit = self.db.get_or_404(self.Workout, workout_id)
        exercises = self.get_exercises(workout_id)
        ex_to_switch = [ex for ex in exercises if ex.id == exercise_id][0]
        ex_index = exercises.index(ex_to_switch)
        if direction == "up" and ex_index != 0:
            exercises.pop(ex_index)
            exercises.insert(ex_index-1, ex_to_switch)
        elif direction == "down" and ex_index != len(exercises)-1:
            exercises.pop(ex_index)
            exercises.insert(ex_index + 1, ex_to_switch)

        new_exercises = []
        for ex in exercises:
            new_exercises.append(f"{ex.id}|{ex.name}")
        workout_to_edit.exercises = str(new_exercises)
        self.db.session.commit()
