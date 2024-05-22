from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField, SelectField, IntegerRangeField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange

from workout_boundaries import TYPES, EQUIPMENT


# WTForm for creating an exercise
class CreateExerciseForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=50)])
    description = TextAreaField("Description", validators=[Length(max=250)], render_kw={'rows': 5})
    type = SelectField("Type", choices=TYPES)
    partner_required = RadioField("Partner required", choices=[(False, "no"), (True, "yes")], default=False)
    equipment = SelectField("Equipment", choices=[("none", "No equipment")]+EQUIPMENT, default="No equipment")
    difficulty = IntegerRangeField("Difficulty", validators=[NumberRange(min=0, max=4)], default=3)
    favourite = RadioField("Favourite", choices=[(False, "no"), (True, "yes")], default=False)
    submit = SubmitField("Submit")


# WTForm for creating a generated workout
class CreateWorkoutForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=20, message="Max Length of Title is 20 symbols")])
    description = TextAreaField("Description", validators=[Length(max=250)], render_kw={'rows': 5})
    stations = IntegerField("Number of exercises", validators=[DataRequired(), NumberRange(min=1, max=60)])
    min_difficulty = IntegerRangeField("Min Difficulty", validators=[NumberRange(min=0, max=4)],
                                       default=0)
    max_difficulty = IntegerRangeField("Max Difficulty", validators=[NumberRange(min=0, max=4)],
                                       default=4)
    dont_repeat = RadioField("Don't repeat exercises", choices=[(False, "no"), (True, "yes")], default=True)
    equipment_required = RadioField("Use Equipment", choices=[(False, "no"), (True, "yes")], default=False)
    fav_only = RadioField("Only favourite exercises", choices=[(False, "no"), (True, "yes")], default=False)
    partner_workout = RadioField("Partnerworkout", choices=[(False, "no"), (True, "yes")], default=False)
    favourite = RadioField("Favourite", choices=[(False, "no"), (True, "yes")], default=False)
    submit = SubmitField("Submit")


# WTForm for creating a custom workout
class CreateCustomWorkoutForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=20, message="Max Length of Title is 20 symbols")])
    description = TextAreaField("Description", validators=[Length(max=250)], render_kw={'rows': 5})
    partner_workout = RadioField("Partnerworkout", choices=[(False, "no"), (True, "yes")], default=False)
    favourite = RadioField("Favourite", choices=[(False, "no"), (True, "yes")], default=False)
    submit = SubmitField("Add Exercises")


class EditWorkoutForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=3, max=20, message="Max Length of Title is 20 symbols")])
    description = TextAreaField("Description", validators=[Length(max=250)], render_kw={'rows': 5})
    favourite = RadioField("Favourite", choices=[(False, "no"), (True, "yes")], default=False)
    submit = SubmitField("Show Exercises")
