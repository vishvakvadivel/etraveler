from flask import (
    Flask,
    render_template,
    url_for,
    flash,
    redirect,
    request,
    session,
)  # imports the necessary flask functions
from flask_mysql_connector import (
    MySQL,
)  # imports the mysql package that allows connection for Flask Apps
from datetime import (
    date,
    timedelta,
)  # imports datetime object and methods for recording dates
import chart_studio  # package that
import plotly.offline as py
import plotly.express as px
import sqlalchemy as alc
import json
import pickle
from Database import *
from forms import (
    StartForm,
    EndForm,
    RejectForm,
    AddOpForm,
    RemoveOpForm,
    FilterForm,
    HomeForm,
    ExcelForm,
)

app = Flask(__name__)

app.config["MYSQL_HOST"] = "45.33.72.29"
app.config["MYSQL_USER"] = "vishvak"  # connection string for database
app.config["MYSQL_PASSWORD"] = "vishvakshaya05"
app.config["MYSQL_DATABASE"] = "processdb"
app.config[
    "SECRET_KEY"
] = "fc6908cce72e555c4ba2384e6a3a08dc"  # secret key for application, needed for Flask sessions

sql = MySQL(app)

# list of process steps
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
tools = Tools()

etrav_dict = {}


class Etraveler:
    def __init__(self, form):
        self.form = form

    def home_page(self):
        if request.method == "POST":  # checks if post request is recieved
            work_order = self.form.order.data.strip()  # gets work order
            process_step = self.form.initstep.data.strip()  # gets initial step
            start_time = datetime.datetime.now()  # gets the current time
            current_quantity = tools.get_current_qty(
                work_order
            )  # gets the current quantity of work order
            etrav_dict[work_order] = [
                start_time,
                process_step,
                current_quantity,
            ]  # puts process values in dictionary
            pickle_out = open(
                "startdata.pickle", "wb"
            )  # creates and opens pickle file to store dictionary
            pickle.dump(etrav_dict, pickle_out)  # dumps the dictionary into pickle file
            pickle_out.close()  # closes pickle file
            redirect_url = url_for("ProcessStart")
            return redirect(f"{redirect_url}?workorder={work_order}")

    def process_start(self):
        if request.method == "POST":
            wo = self.form.workorder.data.strip()  # gets work order from the form
            pn = self.form.partnum.data.strip()  # gets part number
            startqty = self.form.starttrayqty.data  # gets starting tray quantity
            endqty = self.form.endtray.data  # gets the ending tray quantity
            dd = self.form.duedate.data  # gets due date
            split = self.form.barcodestart.data.strip()  # gets the process step
            alpha = self.form.start.data  # gets the start time thats autopopulated

            startstring = alpha.strftime(
                "%H:%M"
            )  # formats the time with hours and minutes

            startlist = startstring.split(
                ":"
            )  # splits the string between hours and minutes
            beta = datetime.datetime.now()  # gets the current time
            cur = sql.connection.cursor()  # creates cursor and connection to database

            duration = beta - timedelta(
                hours=int(startlist[0]), minutes=int(startlist[1])
            )  # measures the duration of time between start and of process

            elapsedtime = duration.time().strftime(
                "%H:%M:%S"
            )  # formats the elapsed time in hours:minutes:seconds

            op = self.form.operator.data.strip()  # gets the operator

            # getop = isoperator(
            #     op, split
            # )  # checks if operator is trained for the specific pricess step

            today = date.today()  # gets the current date
            currentdate = today.strftime("%m/%d/%y")  # formats date

            # if (
            #     arduinoconnect() == True
            # ):  # checks to see if the arduino is connected
            #   arduinovar = (
            #     getvalues()

            # )  # gets the pH, Temperature, and Humidity from arduino sensors
            # today = date.today()  # gets the current date
            # currentdate = today.strftime("%m/%d/%y")  # formats date

            # pH = arduinovar[0]  # indexes list to pH
            # temp = arduinovar[1]  # indexes list for temp
            # hum = arduinovar[2]  # indexes list for humidity

            # cur.execute(
            #   "INSERT INTO enviornmentvariables (pH, Temperature, Humidity, ProcessStep, Date) VALUES (%s, %s, %s, %s, %s)",
            #    (pH, temp, hum, split, currentdate),
            # )  # inserts pH, temp, and humidity into the environment table

            db_connection = alc.create_engine(
                tools.db_connection_str
            )  # creates the actual connection

            query = "SELECT * FROM {}".format(
                "processstep"
            )  # sql query to select all values from the processstep table
            df = pd.read_sql(
                query, con=db_connection
            )  # creates actual connection to server

            index = steplist.index(split)  # gets index of the submitted process step

            if (
                index == 0
            ):  # checks to see if the step is the first step, meaning there are no previous steps
                cur.execute(
                    "INSERT INTO processstep (WorkOrder, P_N, OriginalTrayQty, FinalTrayQty, Operator, Step, Duration, Date, Due_Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",
                    (
                        wo,
                        pn,
                        startqty,
                        endqty,
                        op,  # values to be entered
                        split,
                        elapsedtime,
                        currentdate,
                        dd,
                    ),
                )  # insets the process data into the process table
                sql.connection.commit()  # commits to make changes permanent
                cur.close()  # closes cursor
                flash(
                    "Process Ended, Data Successfully Collected", "success"
                )  # flashes message for success of collection
                del etrav_dict[wo]
                pickle_out = open(
                    "startdata.pickle", "wb"
                )  # creates and opens pickle file to store dictionary
                pickle.dump(
                    etrav_dict, pickle_out
                )  # dumps the dictionary into pickle file
                pickle_out.close()  # closes pickle file
                return redirect(url_for("Home"))  # redericts to the url for home

            previousstep = steplist[
                index - 1
            ]  # gets previous step by subtracting 1 from the index of the submitted step

            if (
                (df["WorkOrder"] == wo) & (df["Step"] == previousstep)
            ).any():  # checks to see if previous process data exists for current work order
                if endqty != tools.reject_check(
                    wo
                ):  # checks if submitted end quatity is accurate
                    flash(
                        "Final Tray Quantity Is Incorrect, Please Review Rejection Data",  # flashes danger message
                        "danger",
                    )
                    return redirect(url_for("Home"))  # redirects to url for home
                cur.execute(
                    "INSERT INTO processstep (WorkOrder, P_N, OriginalTrayQty, FinalTrayQty, Operator, Step, Duration, "
                    "Date, Due_Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)",
                    # sql query to enter process values into table
                    (
                        wo,
                        pn,
                        startqty,
                        endqty,
                        op,
                        split,
                        elapsedtime,  # values to be entered
                        currentdate,
                        dd,
                    ),
                )  # insets the process data into the process table
                sql.connection.commit()  # commits to make changes permanent
                cur.close()  # closes cursor
                flash(
                    "Process Ended, Data Successfully Collected", "success"
                )  # flashes message for success of collection

                del etrav_dict[wo]
                pickle_out = open(
                    "startdata.pickle", "wb"
                )  # creates and opens pickle file to store dictionary
                pickle.dump(
                    etrav_dict, pickle_out
                )  # dumps the dictionary into pickle file
                pickle_out.close()  # closes pickle file

                return redirect(url_for("Home"))  # redericts to the url for home
            else:  # if previous process step work order is not there then it redirects and asks for submission
                flash(
                    f"Previous Step {previousstep} Missing, Please Enter Data", "danger"
                )  # flashes message for success of collection
                return redirect(url_for("Home"))  # redericts to the url for home

    def reject_analysis(self):
        if request.method == "POST":  # checks to see if post request was recieved
            work_order = self.form.wo.data.strip()  # gets work order from form
            partnumber = self.form.pn.data.strip()  # gets part number
            partqty = self.form.rejectionqty.data  # gets numbers of parts rejected
            rejcode = self.form.rejectioncode.data.strip()  # gets rejection code
            op = self.form.op.data.strip()  # gets the operator
            prostep = self.form.step.data.strip()  # gets the process step
            dued = self.form.duedate.data  # gets due date

            # whoisop = isoperator(
            #     op, prostep
            # )  # makes sure that operator is trained in the process step

            day = date.today()  # gets the current date
            currentday = day.strftime("%m/%d/%y")  # formats date

            cur = sql.connection.cursor()  # makes cursor

            cur.execute(
                "INSERT INTO rejectiondata (WorkOrder, P_N, RejCode, Quantity, Operator, ProcessStep, Date, Due_Date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    work_order,
                    partnumber,
                    rejcode,
                    partqty,
                    op,
                    prostep,
                    currentday,
                    dued,
                ),
            )  # enters rejection data into the step

            sql.connection.commit()  # commits changes to database
            cur.close()  # closes cursor

            flash(
                f"Rejection Data Successfully Collected", "success"
            )  # flashes message for succes of collection

            redirect_url = url_for("ProcessStart")
            return redirect(f"{redirect_url}?workorder={work_order}")

    def process_display(self):
        pd.set_option(
            "display.width", 1000
        )  # sets the display width of the pandas dataframe
        pd.set_option("colheader_justify", "center")  # centers the headers

        data = tools.processpdf(
            "processstep"
        )  # creates dataframe for the process table

        return data

    def rejection_display(self):
        pd.set_option("display.width", 1000)
        pd.set_option("colheader_justify", "center")

        data = tools.processpdf("rejectiondata")  # creates dataframe for rejectiondata

        return data

    def environment_display(self):
        pd.set_option("display.width", 1000)
        pd.set_option("colheader_justify", "center")

        data = tools.processpdf(
            "enviornmentvariables"
        )  # creates dataframe for environment table

        return data

    def add_op(self):
        if request.method == "POST":  # checks if post request received
            if (
                self.form.pswd.data.strip() == "Fitch123"
            ):  # checks if admin password the entered was correct
                tools.newop(
                    self.form.newop.data.strip(), self.form.step.data.strip()
                )  # adds new op to training matrix
                name = self.form.newop.data.strip()  # gets operator name
                step = self.step.data.strip()  # gets step name
                flash(
                    f"Operator {name} Has Been Successfully Added to Process Step {step}",
                    "success",
                )  # flashes success mesage whith operator name and process step
                return redirect(url_for("addop"))  # refreshes page

    def rem_op(self):
        if request.method == "POST":  # checks to see if psot method was recieved
            if (
                self.form.pswd.data.strip() == "Fitch123"
            ):  # checks to see if admin password that was entered matched
                tools.lessop(
                    self.form.remop.data.strip(), self.form.step.data.strip()
                )  # removes operator from training matrix
                name = self.form.remop.data.strip()  # gets name
                step = self.form.step.data.strip()  # gets operator
                flash(
                    f"Operator {name} Has Been Successfully Removed From Process Step {step}",
                    "success",
                )  # flashes success message
                return redirect(url_for("remop"))  # refreshes page

    def process_filter(self):
        if request.method == "POST":
            pd.set_option("display.width", 1000)  # display width
            pd.set_option("colheader_justify", "center")  # centers headers

            firstfield = (
                self.form.categoryone.data.strip().lower()
            )  # gets first table column
            firstvalue = (
                self.form.valueone.data.strip()
            )  # gets first value from first column

            secondfield = (
                self.form.categorytwo.data.strip().lower()
            )  # gets second table column
            secondvalue = (
                self.form.valuetwo.data.strip()
            )  # gets second value for second column

            newdf = tools.propdfilter(
                firstfield, firstvalue, "processstep", secondfield, secondvalue
            )  # creates a dataframe filtered for the two specific column values

            return render_template(
                "pandasdisplay.html",
                title="Filter Data",
                table=newdf.to_html(classes="mystyle", index=False),
            )  # renders html template and injects variables

    def rejection_filter(self):
        if request.method == "POST":  # check if post method was recieved
            pd.set_option(
                "display.width", 1000
            )  # sets display width for pandas dataframe
            pd.set_option("colheader_justify", "center")  # centers the column headers

            firstfield = (
                self.form.categoryone.data.strip().lower()
            )  # gets the the first category for the filter by picking a table column
            firstvalue = (
                self.form.valueone.data.strip()
            )  # picks a vlaue to search for in that column

            secondfield = (
                self.form.categorytwo.data.strip().lower()
            )  # gets a second column value
            secondvalue = (
                self.form.valuetwo.data.strip()
            )  # gets value to search for in the second value

            newdf = tools.rejpdfilter(
                firstfield, firstvalue, "rejectiondata", secondfield, secondvalue
            )  # creates a filtered dataframe with the two specific column values

            return render_template(
                "pandasdisplay.html",
                title="Filter Data",
                table=newdf.to_html(classes="mystyle", index=False),
            )  # renders html template and injects variables

    def yield_graph(self):

        db_connection = alc.create_engine(
            tools.db_connection_str
        )  # creates the actual connection

        query = "SELECT * FROM {}".format(
            "processstep"
        )  # sql query to select all values from the processstep table

        df = pd.read_sql(
            query, con=db_connection
        )  # creates actual connection to server

        iter_part_numbers = (
            df.P_N.unique().tolist()
        )  # finds and creates list of  unique part number values in P_N column for iteration in for loop
        df_part_numbers = (
            df.P_N.unique().tolist()
        )  # seperate list created for unique part numbers to be put into dataframe
        pn_yield = []  # empty list that will hold p/n yield

        for (
            pn
        ) in iter_part_numbers:  # iterates through all the part numbers in the list

            original_quantity = df.loc[
                (df["P_N"] == pn)
                & (
                    df["Step"] == "Preclean"
                ),  # gathers the original tray quantities for the part number at preclean, which is the start of the process, and sums them up
                "OriginalTrayQty",
            ].sum()

            final_quantity = df.loc[
                (df["P_N"] == pn)
                & (
                    df["Step"] == "Packaging"
                ),  # gathers the final tray quantities at packaging, which is always the last step in the process, and sums them
                "FinalTrayQty",
            ].sum()

            if (
                original_quantity == 0
            ):  # checks to see if total original quantity is 0, to avoid divide by 0 error
                df_part_numbers.remove(
                    pn
                )  # removes part number from list to be put in dataframe
                continue  # skips to next iteration

            pn_yield.append(  # appends value to yield list
                final_quantity
                / original_quantity  # divides final quantity by original quantity to get yield
            )

        pn_and_yield = list(
            zip(
                df_part_numbers, pn_yield
            )  # creates list of tuples with the part numbers and corresponding yields
        )

        yield_df = pd.DataFrame(
            pn_and_yield,
            columns=["Part Number", "Yield"],  # creates dataframe from list of tuples
        )

        fig = px.bar(
            yield_df, x="Part Number", y="Yield"
        )  # creates the graph from the dataframe with plotly
        fig.update_layout(title="P/N Yield")  # adds title
        fig.update_layout(yaxis=dict(tickformat=".2%"))  # makes y axis have percentage

        username = "vishvak_vadivel"  # username for account
        api_key = "FgcrQz161n6ZLfgsg7YH"  # api key store and create graph

        html_str = py.plot(
            fig, include_plotlyjs=False, output_type="div"
        )  # plots the graph and outputs html div

        return html_str

    def rejection_graph(self):
        db_connection = alc.create_engine(
            tools.db_connection_str
        )  # creates actual connection to database

        query = "SELECT * FROM {}".format(
            "rejectiondata"
        )  # sql query to select all table data for the rejectiondata table

        df = pd.read_sql(
            query, con=db_connection
        )  # creates pandas dataframe from sql table

        fig = px.bar(
            df, x="RejCode", y="Quantity", hover_data=["ProcessStep", "Date"]
        )  # creates plotly bar chart and chosses hover data
        fig.update_layout(title="Rejection Data")  # sets title
        fig.update_xaxes(tickangle=40)
        username = "vishvak_vadivel"  # username for plotly account
        api_key = "FgcrQz161n6ZLfgsg7YH"  # api key generated from plotly account

        html_str = py.plot(
            fig, include_plotlyjs=False, output_type="div"
        )  # plots the graph and outputs html div

        return html_str

    def download(self):
        if request.method == "POST":  # checks if post request

            db_connectrion_str = "mysql+pymysql://oaks:123Vish@192.168.77.37/gratingsdb"  # connection string

            db_connection = alc.create_engine(
                db_connectrion_str
            )  # creates actual connection to database

            query = "SELECT * FROM {}".format(
                "processstep"
            )  # sql query to gather all the data from the processstep table

            df = pd.read_sql(query, con=db_connection)  # creates df
            writer = pd.ExcelWriter("processdata.xlsx")  # makes excel file

            df.to_excel(writer, sheet_name="bar")  # converts the dataframe to excel
            writer.save()  # saves excel file

            flash(f"Excel File Downloaded", "success")  # flashes message for success

            return redirect(url_for("download"))  # refreshes the page


@app.route(
    "/", methods=["GET", "POST"]
)  # created home route for app with get and post methods
def Home():
    form = HomeForm()  # creates form object
    if request.method == "GET":
        return render_template(
            "Home.html", title="Home", form=form
        )  # renders html template and injects variables
    if request.method == "POST":
        home = Etraveler(form)
        return home.home_page()


@app.route(
    "/ProcessAnalysisStart", methods=["GET", "POST"]
)  # created process start route for app with get and post methods
def ProcessStart():
    try:
        work_order = request.args.get("workorder")
        autofill_data = tools.processautofill(
            work_order
        )  # gathers autofill data for work order, part number, and due date and puts into list
        part_number = autofill_data[0]  # gets part number
        due_date = autofill_data[1]  # gets due date
        pickle_in = open("startdata.pickle", "rb")
        start_data = pickle.load(pickle_in)
        start_time = start_data.get(work_order)[0]
        process_step = start_data.get(work_order)[1]
        start_qty = start_data.get(work_order)[2]

    except TypeError:
        form = StartForm()
        return render_template(
            "ProcessStart.html", title="Process Start", form=form
        )  # renders html template and injects variables

    form = StartForm(
        workorder=work_order,
        partnum=part_number,
        starttrayqty=start_qty,
        duedate=due_date,
        endtray=tools.reject_check(work_order),
        barcodestart=process_step,
        start=start_time,
    )  # pass in values of auto fill list

    if request.method == "GET":
        return render_template(
            "ProcessStart.html", title="Process Start", form=form
        )  # renders html template and injects variables

    if request.method == "POST":
        start_page = Etraveler(form)
        return start_page.process_start()


@app.route(
    "/RejectionAnalysis", methods=["GET", "POST"]
)  # creates url and route for rejection data collection
def RejectAnalysis():
    form = RejectForm()  # creates form object

    if request.method == "GET":
        return render_template(
            "RejectionEntry.html", title="Rejection Data Entry", form=form
        )  # renders html template and injects variables

    if request.method == "POST":
        reject_page = Etraveler(form)
        return reject_page.reject_analysis()


@app.route(
    "/ProcessTable", methods=["GET", "POST"]
)  # creates route to display the process table
def processdisplay():
    process_display_page = Etraveler(None)
    if request.method == "GET":
        return render_template(
            "pandasdisplay.html",
            title="Process Step Table",
            table=process_display_page.process_display().to_html(
                classes="mystyle", index=False
            ),
        )  # renders html template, converts the data frame to html, adds css formatting and injects variables


@app.route(
    "/RejectionTable", methods=["GET", "POST"]
)  # creates the route for the display of the rejection table
def rejectdisplay():
    reject_display_page = Etraveler(None)
    if request.method == "GET":
        return render_template(
            "pandasdisplay.html",
            title="Rejection Table",
            table=reject_display_page.rejection_display().to_html(
                classes="mystyle", index=False
            ),
        )  # renders html template, converts the data frame to html, adds css formatting and injects variables


@app.route(
    "/EnvironmentTable", methods=["GET", "POST"]
)  # creates route for display of the environment table
def enviornmentdisplay():
    environment_display_page = Etraveler(None)
    if request.method == "GET":
        return render_template(
            "pandasdisplay.html",
            title="Enviornment Table",
            table=environment_display_page.environment_display().to_html(
                classes="mystyle", index=False
            ),
        )  # renders html template, converts the data frame to html, adds css formatting and injects variables


@app.route("/AddOp", methods=["GET", "POST"])  # creates route to add operator
def addop():
    form = AddOpForm()
    if request.method == "GET":
        return render_template(
            "AddOp.html", title="Add Operator", form=form
        )  # renders html template and injects variables

    if request.method == "POST":
        add_op_page = Etraveler(form)
        return add_op_page.add_op()


@app.route(
    "/RemOp", methods=["GET", "POST"]
)  # creates route to remove operator from training matrix
def remop():
    form = RemoveOpForm()  # creates form object

    if request.method == "GET":
        return render_template(
            "RemOp.html", title="Remove Operator", form=form
        )  # renders html template and injects variables

    if request.method == "POST":
        rem_op_page = Etraveler(form)
        return rem_op_page.rem_op()


@app.route(
    "/ProcessFilter", methods=["GET", "POST"]
)  # creates route to for process table filter
def profilter():
    form = FilterForm()  # creates a form object

    if request.method == "GET":
        return render_template(
            "FilterForm.html", title="Filter Data", form=form
        )  # renders html template and injects variables

    if request.method == "POST":
        process_filter_page = Etraveler(form)
        return process_filter_page.process_filter()


@app.route(
    "/RejectionFilter", methods=["GET", "POST"]
)  # creates route for filter of rejection data
def rejfilter():
    form = FilterForm()  # creates form object

    if request.method == "GET":
        return render_template(
            "FilterForm.html", title="Filter Data", form=form
        )  # renders html template and injects variables

    if request.method == "POST":
        rejection_filter_page = Etraveler(form)
        return rejection_filter_page.rejection_filter()


@app.route(
    "/PartNumberYield", methods=["GET", "POST"]
)  # creates route for p/n yield graph
def yieldgraph():  # must change how yield is calculated
    yield_page = Etraveler(None)

    if request.method == "GET":
        return render_template(
            "GraphDisplay.html", title="Yield Graph", plot=yield_page.yield_graph()
        )  # renders html template and injects variables


@app.route(
    "/RejectionGraph", methods=["GET", "POST"]
)  # creates route for rejection graph
def rejgraph():
    rejection_graph_page = Etraveler(None)

    if request.method == "GET":
        return render_template(
            "GraphDisplay.html",
            title="Rejection Graph",
            plot=rejection_graph_page.rejection_graph(),
        )  # renders html template and injects the embedded text


@app.route("/download", methods=["GET", "POST"])  # creates download route
def download():
    form = ExcelForm()  # creates form object

    if request.method == "GET":
        return render_template(
            "Excel.html", form=form
        )  # renders template and establishes the form

    if request.method == "POST":
        download_page = Etraveler(form)
        return download_page.download()


if __name__ == "__main__":  # makes the app run
    app.run(debug=True, threaded=True)
