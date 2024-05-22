from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
from flask_bootstrap import Bootstrap5

from forms import CreateExerciseForm, CreateWorkoutForm, CreateCustomWorkoutForm, EditWorkoutForm
from utils import to_bool, transform_attributes, spruce_up_exercises
from generator import generate_workout
from workout_manager import WorkoutManager


COLOR_MODE = "dark"
EXERCISE_FILTER = {
    "last": "favourite_desc",
    "current": "favourite_desc"
}
WORKOUT_FILTER = "favourite"


app = Flask(__name__)
app.config['SECRET_KEY'] = "8BYkEfBA6O6donzWlSihBXox7C0sKR6b"


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///workout_generator.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)
Bootstrap5(app)


# exercise TABLE Configuration
class Exercise(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    partner_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    favourite: Mapped[bool] = mapped_column(Boolean, nullable=False)
    equipment: Mapped[str] = mapped_column(String(50), nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=False)


# workout TABLE Configuration
class Workout(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=True)
    stations: Mapped[int] = mapped_column(Integer, nullable=True)
    difficulty: Mapped[int] = mapped_column(Integer, nullable=True)
    partner_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    equipment: Mapped[str] = mapped_column(String(50), nullable=True)
    exercises: Mapped[str] = mapped_column(String(2000), nullable=True)
    favourite: Mapped[bool] = mapped_column(Boolean, nullable=False)


with app.app_context():
    db.create_all()


workout_manager = WorkoutManager(db, Workout, Exercise)


def query_db():
    match EXERCISE_FILTER['current']:
        case "type":
            return db.session.execute(db.select(Exercise).order_by(Exercise.type))
        case "type_desc":
            return db.session.execute(db.select(Exercise).order_by(Exercise.type.desc()))
        case "difficulty":
            return db.session.execute(db.select(Exercise).order_by(Exercise.difficulty))
        case "difficulty_desc":
            return db.session.execute(db.select(Exercise).order_by(Exercise.difficulty.desc()))
        case "favourite":
            return db.session.execute(db.select(Exercise).order_by(Exercise.favourite, Exercise.partner_required))
        case "favourite_desc":
            return db.session.execute(db.select(Exercise).order_by(Exercise.favourite.desc(), Exercise.partner_required.desc()))
        case "name":
            return db.session.execute(db.select(Exercise).order_by(Exercise.name))
        case "name_desc":
            return db.session.execute(db.select(Exercise).order_by(Exercise.name.desc()))
        case "equipment":
            return db.session.execute(db.select(Exercise).order_by(Exercise.equipment))
        case "equipment_desc":
            return db.session.execute(db.select(Exercise).order_by(Exercise.equipment.desc()))
        case _:
            return db.session.execute(db.select(Exercise).order_by(Exercise.type))


@app.route("/")
def home():
    return render_template("index.html", color_mode=COLOR_MODE, redirect_url="home")


@app.route("/switch-color/<string:redirect_url>", methods=["GET", "POST"])
def switch_color(redirect_url):
    global COLOR_MODE
    COLOR_MODE = "light" if COLOR_MODE == "dark" else "dark"
    return redirect(url_for(redirect_url))


@app.route("/switch_exercise_filter/<string:new_filter>/<string:redirect_url>/")
@app.route("/switch_exercise_filter/<string:new_filter>/<string:redirect_url>/<int:workout_id>")
def switch_exercise_filter(new_filter, redirect_url, workout_id=""):
    global EXERCISE_FILTER
    EXERCISE_FILTER["last"] = EXERCISE_FILTER["current"]
    EXERCISE_FILTER["current"] = new_filter
    if EXERCISE_FILTER["last"] == EXERCISE_FILTER["current"]:
        EXERCISE_FILTER["current"] = new_filter+"_desc"

    if workout_id == "None":
        return redirect(url_for(redirect_url))
    else:
        return redirect(url_for(redirect_url, workout_id=workout_id))


@app.route("/show_exercises", methods=["GET", "POST"])
def show_exercises():
    result = query_db()
    exercises = result.scalars().all()
    for exercise in exercises:
        exercise.type = transform_attributes(exercise.type)
        exercise.equipment = transform_attributes(exercise.equipment)
    return render_template('exercises.html', color_mode=COLOR_MODE, redirect_url="show_exercises", exercises=exercises)


@app.route("/add-exercise", methods=["GET", "POST"])
def add_exercise():
    form = CreateExerciseForm()
    if form.validate_on_submit():
        new_exercise = Exercise(
            name=form.name.data,
            description=form.description.data,
            type=form.type.data,
            partner_required=to_bool(form.partner_required.data),
            equipment=form.equipment.data,
            difficulty=form.difficulty.data,
            favourite=to_bool(form.favourite.data)
        )
        db.session.add(new_exercise)
        db.session.commit()
        return redirect(url_for('show_exercises'))
    return render_template('add_exercise.html', color_mode=COLOR_MODE, redirect_url="add_exercise", form=form)


@app.route("/edit-exercise/<int:exercise_id>", methods=["GET", "POST"])
def edit_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    edit_form = CreateExerciseForm(
        name=exercise.name,
        description=exercise.description,
        type=exercise.type,
        partner_required=exercise.partner_required,
        equipment=exercise.equipment,
        difficulty=exercise.difficulty,
        favourite=exercise.favourite
    )
    if edit_form.validate_on_submit():
        exercise.name = edit_form.name.data
        exercise.description = edit_form.description.data
        exercise.type = edit_form.type.data
        exercise.partner_required = to_bool(edit_form.partner_required.data)
        exercise.equipment = edit_form.equipment.data
        exercise.difficulty = edit_form.difficulty.data
        exercise.favourite = to_bool(edit_form.favourite.data)
        db.session.commit()
        return redirect(url_for("show_exercises"))
    return render_template("add_exercise.html", color_mode=COLOR_MODE, redirect_url="show_exercises", form=edit_form)


@app.route("/delete/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise_to_delete = db.get_or_404(Exercise, exercise_id)
    db.session.delete(exercise_to_delete)
    db.session.commit()
    return redirect(url_for('show_exercises'))


@app.route("/fav_exercise/<int:exercise_id>")
def fav_exercise(exercise_id):
    exercise = db.get_or_404(Exercise, exercise_id)
    exercise.favourite = not exercise.favourite
    db.session.commit()
    return redirect(url_for("show_exercises"))


@app.route("/show_workouts", methods=["GET", "POST"])
def show_workouts():
    result = db.session.execute(db.select(Workout).order_by(Workout.favourite.desc(), Workout.difficulty.desc()))
    workouts = result.scalars().all()
    workout_exercises = [workout_manager.get_exercises(workout.id) for workout in workouts]
    for workout in workouts:
        workout.equipment = transform_attributes(workout.equipment)

    for workout_exs in workout_exercises:
        for ex in workout_exs:
            ex.equipment = transform_attributes(ex.equipment)

    workout_packages = list(zip(workouts, workout_exercises))

    return render_template('workouts.html', color_mode=COLOR_MODE, redirect_url="show_workouts", workout_packages=workout_packages, len=len)


@app.route("/create-generated-workout", methods=["GET", "POST"])
def create_generated_workout():
    form = CreateWorkoutForm()
    if form.validate_on_submit():
        if form.min_difficulty.data > form.max_difficulty.data:
            # generate_error = "Minimum Difficulty can't be higher, than maximum Difficulty!"
            flash("Minimum Difficulty can't be higher, than maximum Difficulty!")
            return render_template('create_generated_workout.html', color_mode=COLOR_MODE,
                                   redirect_url="create_workout", form=form)
        result = db.session.execute(db.select(Exercise))
        all_exercises = result.scalars().all()
        workout_details = generate_workout(form, all_exercises)

        if not workout_details:
            flash("Not enough different exercises available to generate the workout!")
            return render_template('create_generated_workout.html', color_mode=COLOR_MODE,
                                   redirect_url="create_workout", form=form)
        new_workout = Workout(
            name=form.name.data,
            description=form.description.data,
            stations=form.stations.data,
            difficulty=workout_details[1],
            partner_required=to_bool(form.partner_workout.data),
            equipment=workout_details[2],
            exercises=workout_details[0],
            favourite=to_bool(form.favourite.data)
        )
        db.session.add(new_workout)
        db.session.commit()
        return redirect(url_for('show_workouts'))
    return render_template('create_generated_workout.html', color_mode=COLOR_MODE, redirect_url="create_generated_workout", form=form)


@app.route("/create-custom-workout", methods=["GET", "POST"])
def create_custom_workout():
    form = CreateCustomWorkoutForm()
    if form.validate_on_submit():
        new_workout = Workout(
            name=form.name.data,
            description=form.description.data,
            partner_required=to_bool(form.partner_workout.data),
            favourite=to_bool(form.favourite.data)
        )
        db.session.add(new_workout)
        db.session.commit()
        db.session.flush()
        workout_id = new_workout.id
        return redirect(url_for('workout_exercises', workout_id=workout_id))
    return render_template('create_custom_workout.html', color_mode=COLOR_MODE, redirect_url="create_custom_workout", form=form)


@app.route("/workout-exercises/<int:workout_id>", methods=["GET", "POST"])
def workout_exercises(workout_id):
    result = query_db()
    all_exercises = result.scalars().all()

    workout = db.get_or_404(Workout, workout_id)
    try:
        workout_exercises = workout_manager.get_exercises(workout_id)
    except AttributeError:
        workout_exercises = []
        temp_exercises = [ex for ex in all_exercises]
    else:
        temp_exercises = [ex for ex in all_exercises if ex not in workout_exercises]
    if workout.partner_required:
        feasible_exercises = [ex for ex in temp_exercises if ex.partner_required]
    else:
        feasible_exercises = [ex for ex in temp_exercises if not ex.partner_required]
    return render_template('workout_exercises.html', color_mode=COLOR_MODE, redirect_url="workout_exercises", exercises=spruce_up_exercises(feasible_exercises), workout_exercises=spruce_up_exercises(workout_exercises), workout=workout, enumerate=enumerate)


@app.route("/add-workout-exercise/<int:workout_id>/<int:exercise_id>")
def add_workout_exercise(workout_id, exercise_id):
    workout_manager.add_exercise(workout_id, exercise_id)
    return redirect(url_for('workout_exercises', workout_id=workout_id))


@app.route("/remove-workout-exercise/<int:workout_id>/<int:exercise_id>")
def remove_workout_exercise(workout_id, exercise_id):
    workout_manager.drop_exercise(workout_id, exercise_id)
    return redirect(url_for('workout_exercises', workout_id=workout_id))


@app.route("/switch-workout-exercise/<int:workout_id>/<int:exercise_id>/<direction>")
def switch_workout_exercise(workout_id, exercise_id, direction):
    workout_manager.switch_workout_exercises(workout_id, exercise_id, direction)
    return redirect(url_for('workout_exercises', workout_id=workout_id))


@app.route("/fav_workout/<int:workout_id>")
def fav_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    workout.favourite = not workout.favourite
    db.session.commit()
    return redirect(url_for("show_workouts"))


@app.route("/delete-workout/<int:workout_id>")
def delete_workout(workout_id):
    workout_to_delete = db.get_or_404(Workout, workout_id)
    db.session.delete(workout_to_delete)
    db.session.commit()
    return redirect(url_for('show_workouts'))


@app.route("/edit-workout/<int:workout_id>", methods=["GET", "POST"])
def edit_workout(workout_id):
    workout = db.get_or_404(Workout, workout_id)
    edit_form = EditWorkoutForm(
        name = workout.name,
        description = workout.description,
        favourite = workout.favourite
    )
    if edit_form.validate_on_submit():
        workout.name = edit_form.name.data
        workout.description = edit_form.description.data
        workout.favourite = to_bool(edit_form.favourite.data)
        db.session.commit()
        return redirect(url_for("workout_exercises", workout_id=workout_id))
    return render_template("edit_workout.html", color_mode=COLOR_MODE, redirect_url="show_workouts", form=edit_form)


if __name__ == '__main__':
    app.run(debug=True)
