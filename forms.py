from flask_wtf import (
    FlaskForm,
)  # imports the module we need to make forms in flask
from flask_wtf.file import (
    FileField,
)  # imports module to have a file submission field
from wtforms import (
    StringField,
    SubmitField,
    IntegerField,
    PasswordField,
    SelectField,
    TimeField,
)  # needed for app
from wtforms.validators import (
    DataRequired,
)  # validator that ensures forms aren't blank when submitted
import datetime
import pytz

p_n_list = [
    19204,
    19354,
    19363,
    19366,
    19477,
    19507,
    19536,
    19544,
    19554,
    19555,
    39229,
    39230,
    39283,
    49043,
    49287,
    49431,
    49489,
    49492,
    49540,
    49597,
    49598,
    59024,
    60118,
    60126,
    60145,
]  # part number list

operatorlist = [
    "Leo McGuire",
    "Rith Phal",
    "Tony Inthirath",
    "Heather Tragash",
    "Liz Hernandez",
    "Chance Souvannadeth",
    "Bob Halliday",
    "Melinda Clemens",
    "Michael Paul",
]  # oprerator list

dlist = ["process", "rejection", "environment"]  # table list
errorcodes = [
    "Engineering Experiments",
    "no resist/non-uniform resist",  # error code list
    "Chips/Breakage",
    "Comet",
    "Finger/Glove Print",
    "Haziness",
    "Hologram",
    "Mount Mark Too Large or Placed Wrong",
    "Particulate",
    "Pinhole",
    "Digs",
    "Scratch",
    "Speckle",
    "Maggots",
    "Spit",
    "Stain",
    "Washed Area/Area with no Grating",
    "Vibration/Motion",
    "wiped front",
    "chemical on front",
    "green coat on front",
    "crack line in resist or gold",
    "missing metal in clear aperture",
    "resist coated on wrong side",
    "metal coated on wrong side",
    "bubble in photoresist",
    "bullseye",
    "non-uniform exposure/hotspot",
    "fails process control range-deep",
    "fails process control range-shallow",
    "Not exposed",
    "Bottomed/Washed",
    "double exposed",
    "perpendicularity",
    "wavefront",
    "flatness",
    "photoresist thickness",
    "green coat will not adhere to back side",
    "Drying stain",
    "eyelashes",
    "perpendicularity of cut",
    "perpendicularity of grooves",
    "handling damage",
    "saw damage",
    "fails final test range-low",
    "fails final test range-high",
    "image out of focus",
    "groove perpendicularity",
    "fails stray light laser",
    "fails bandwidth",
    "fails 'no go' gauge",
    "substrate perpendicularity",
    "pdl failure",
    "fails 9um filter shape test",
    "fails groove frequency",
    "fails alignment tester",
    "Equipment failure",
    "metal coating error",
]

# list for process steps, most likely will need to add more
steplist = [
    "Preclean",
    "PR Application",
    "Softbake",
    "Antihalation",
    "Setup for Exposure",
    "Exposure",
    "Preliminary Cosmetic Inspection",
    "Hot UV exposure",
    "Hardbake",
    "Metalization",
    "Pretest Cosmetic Inspection",
    "Final Efficiency Test",
    "Perpendicularity",
    "Flatness",
    "Final Visual Inspection",
    "Stray Light",
    "Packaging",
]

# list for type of filter selection
fl = ["operator", "part number", "work order", "step", "In Process"]

# sets timezone as New York
est = pytz.timezone("America/New_York")


class HomeForm(FlaskForm):  # creates form for home field
    order = StringField(
        "Work Order", validators=[DataRequired()]
    )  # creates work order field
    initstep = SelectField(
        "Process Step", choices=steplist, validators=[DataRequired()]
    )  # creates a dropdown menu to select process step
    submit = SubmitField("Submit")  # submit button


class StartForm(FlaskForm):  # this is for the process start form
    barcodestart = SelectField(
        "Process Step", choices=steplist, validators=[DataRequired()]
    )  # creates drop down menu for process step
    operator = SelectField(
        "Operator", choices=operatorlist, validators=[DataRequired()]
    )  # creates drop down menu for operator
    duedate = StringField(
        "Due Date", validators=[DataRequired()]
    )  # creates field for due date
    starttrayqty = IntegerField(
        "Starting Tray Quantity", validators=[DataRequired()]
    )  # creates field for starting tray quantity
    endtray = IntegerField(
        "Final Tray Quantity", validators=[DataRequired()]
    )  # creates field for ending tray quantity
    workorder = StringField(
        "Work Order", validators=[DataRequired()]
    )  # creates field for work order
    partnum = StringField(
        "Part Number", validators=[DataRequired()]
    )  # creates field for part number
    start = TimeField(
        "Start Time"
    )  # creates starttime field, autofills with current time on refresh
    submit = SubmitField("Submit")  # submit field


class EndForm(FlaskForm):
    endtrayqty = IntegerField("Final Tray Qty", validators=[DataRequired()])
    submit = SubmitField("Submit")


class RejectForm(FlaskForm):  # form for rejection data
    wo = StringField(
        "Work Order", validators=[DataRequired()]
    )  # creates firld for work order
    duedate = StringField(
        "Due Date", validators=[DataRequired()]
    )  # creates firld for due date
    op = SelectField(
        "Operator", choices=operatorlist, validators=[DataRequired()]
    )  # creates drop down for operators
    pn = SelectField(
        "Part Number", choices=p_n_list, validators=[DataRequired()]
    )  # creates drop down for part numbers
    rejectionqty = IntegerField(
        "Quantity of Parts Rejected ", validators=[DataRequired()]
    )  # creates field for rejection quatity
    rejectioncode = SelectField(
        "Rejection Code", choices=errorcodes, validators=[DataRequired()]
    )  # creates drop down for rejection code
    step = SelectField(
        "Process Step", choices=steplist, validators=[DataRequired()]
    )  # creates drop down for process step
    submit = SubmitField("Submit")  # creates submit field


class AddOpForm(FlaskForm):  # form to add operator
    step = StringField(
        "What Step Are You Adding To?", validators=[DataRequired()]
    )  # creates firld for processs step
    newop = StringField(
        "Who Is The Operator Being Added?", validators=[DataRequired()]
    )  # creates field for operator being added
    pswd = PasswordField(
        "Please Enter Admin Password", validators=[DataRequired()]
    )  # creates password field for admin password
    submit = SubmitField("Submit")  # creates submit field


class RemoveOpForm(FlaskForm):  # form to remove operator
    step = StringField(
        "What Step Are You Removing From?", validators=[DataRequired()]
    )  # creates firld for process step
    remop = StringField(
        "Who Is The Operator Being Removed?", validators=[DataRequired()]
    )  # creates firld for operator being removed
    pswd = PasswordField(
        "Please Enter Admin Password", validators=[DataRequired()]
    )  # creates firld for admin password
    submit = SubmitField("Submit")  # creates submit field


class FilterForm(FlaskForm):  # form to filter

    categoryone = SelectField(
        "What is the first category you are filtering by?",
        choices=fl,
        validators=[DataRequired()],
    )  # creates a drop down menu for the first filter category
    categorytwo = SelectField(
        "What is the second category you are filtering by?",
        choices=fl,
        validators=[DataRequired()],
    )  # creates a second drop down menu for the second filter category
    valueone = StringField(
        "What is the value you are filtering for?"
    )  # creates field for first category value
    valuetwo = StringField(
        "What is the value you are filtering for?"
    )  # creates field for second category value
    submit = SubmitField("Filter Data")  # creates submit field


class UploadForm(FlaskForm):
    file = FileField()


class ExcelForm(FlaskForm):
    table = SelectField(
        "What Table Should Be Downloaded?",
        validators=[DataRequired()],
        choices=dlist,
    )  # creates field to select table
    submit = SubmitField("Submit")  # submit field
