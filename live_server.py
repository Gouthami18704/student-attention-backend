from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import csv
import os
import threading

app = Flask(__name__)
CORS(app)

# ============================================================
# CONFIGURATION
# ============================================================

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", 5000))

DATA_DIR = "WACV data"
LIVE_DATA_FILE = os.path.join(DATA_DIR, "live_student_data.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# Stores latest information of every student
students = {}

# Thread safety for multiple students
data_lock = threading.Lock()


# ============================================================
# CSV INITIALIZATION
# ============================================================

def initialize_csv():

    if not os.path.exists(LIVE_DATA_FILE):

        with open(
            LIVE_DATA_FILE,
            "w",
            newline="",
            encoding="utf-8"
        ) as file:

            writer = csv.writer(file)

            writer.writerow([
                "timestamp",
                "student_id",
                "student_name",
                "email",
                "attention_score",
                "attention_status",
                "predicted_class",
                "attendance",
                "alerts",
                "recommendation",
                "distractions",
                "transitions",
                "stability"
            ])


initialize_csv()


# ============================================================
# HOME / SERVER TEST
# ============================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "status": "success",
        "message": "Student Attention Live Server is running",
        "server": "Flask",
        "port": PORT
    })


# ============================================================
# STUDENT LOGIN / JOIN CLASS
# ============================================================

@app.route("/student/join", methods=["POST"])
def student_join():

    try:

        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "No student data received"
            }), 400

        student_id = str(
            data.get("student_id", "")
        ).strip()

        student_name = str(
            data.get("student_name", "")
        ).strip()

        email = str(
            data.get("email", "")
        ).strip()

        if not student_id:
            return jsonify({
                "status": "error",
                "message": "student_id is required"
            }), 400

        if not student_name:
            return jsonify({
                "status": "error",
                "message": "student_name is required"
            }), 400

        if not email:
            return jsonify({
                "status": "error",
                "message": "email is required"
            }), 400

        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        student_data = {

            "student_id": student_id,

            "student_name": student_name,

            "email": email,

            "attention_score": 0.0,

            "attention_status": "WAITING",

            "predicted_class": -1,

            "attendance": "Present",

            "alerts": 0,

            "recommendation":
                "Waiting for attention analysis...",

            "distractions": 0,

            "transitions": 0,

            "stability": "UNKNOWN",

            # Nudge information
            "nudge": None,

            "joined_at": now,

            "last_update": now
        }

        with data_lock:

            students[student_id] = student_data

        return jsonify({

            "status": "success",

            "message":
                "Student joined the online class",

            "student": student_data

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500


# ============================================================
# RECEIVE LIVE ATTENTION DATA
# ============================================================

@app.route("/student/update", methods=["POST"])
def student_update():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "status": "error",

                "message":
                    "No attention data received"

            }), 400

        student_id = str(
            data.get("student_id", "")
        ).strip()

        if not student_id:

            return jsonify({

                "status": "error",

                "message":
                    "student_id is required"

            }), 400

        with data_lock:

            # If student does not exist,
            # create a basic record

            if student_id not in students:

                students[student_id] = {

                    "student_id":
                        student_id,

                    "student_name":
                        data.get(
                            "student_name",
                            "Unknown"
                        ),

                    "email":
                        data.get(
                            "email",
                            ""
                        ),

                    "attention_score":
                        0.0,

                    "attention_status":
                        "WAITING",

                    "predicted_class":
                        -1,

                    "attendance":
                        "Present",

                    "alerts":
                        0,

                    "recommendation":
                        "Waiting for attention analysis...",

                    "distractions":
                        0,

                    "transitions":
                        0,

                    "stability":
                        "UNKNOWN",

                    "nudge":
                        None,

                    "joined_at":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),

                    "last_update":
                        datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                }

            student = students[student_id]

            # Update only supplied values

            if "student_name" in data:

                student["student_name"] = \
                    data["student_name"]

            if "email" in data:

                student["email"] = \
                    data["email"]

            if "attention_score" in data:

                student["attention_score"] = float(
                    data["attention_score"]
                )

            if "attention_status" in data:

                student["attention_status"] = \
                    data["attention_status"]

            if "predicted_class" in data:

                student["predicted_class"] = int(
                    data["predicted_class"]
                )

            if "alerts" in data:

                student["alerts"] = int(
                    data["alerts"]
                )

            if "recommendation" in data:

                student["recommendation"] = \
                    data["recommendation"]

            if "distractions" in data:

                student["distractions"] = int(
                    data["distractions"]
                )

            if "transitions" in data:

                student["transitions"] = int(
                    data["transitions"]
                )

            if "stability" in data:

                student["stability"] = \
                    data["stability"]

            student["last_update"] = \
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # Save current information to CSV

            with open(
                LIVE_DATA_FILE,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([

                    student["last_update"],

                    student["student_id"],

                    student["student_name"],

                    student["email"],

                    student["attention_score"],

                    student["attention_status"],

                    student["predicted_class"],

                    student["attendance"],

                    student["alerts"],

                    student["recommendation"],

                    student["distractions"],

                    student["transitions"],

                    student["stability"]
                ])

        return jsonify({

            "status": "success",

            "message":
                "Attention data updated",

            "student": student

        })

    except Exception as e:

        return jsonify({

            "status": "error",
            "message": str(e)

        }), 500


# ============================================================
# SEND NUDGE TO STUDENT
# ============================================================

@app.route("/student/nudge", methods=["POST"])
def student_nudge():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "status": "error",

                "message":
                    "No nudge data received"

            }), 400

        student_id = str(
            data.get("student_id", "")
        ).strip()

        if not student_id:

            return jsonify({

                "status": "error",

                "message":
                    "student_id is required"

            }), 400

        message = str(
            data.get(
                "message",
                "Your instructor suggests focusing on the class."
            )
        ).strip()

        with data_lock:

            if student_id not in students:

                return jsonify({

                    "status": "error",

                    "message":
                        "Student not found"

                }), 404

            students[student_id]["nudge"] = {

                "message": message,

                "timestamp":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "read": False
            }

        return jsonify({

            "status": "success",

            "message":
                "Nudge sent successfully",

            "nudge": {

                "student_id":
                    student_id,

                "message":
                    message
            }

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message":
                str(e)

        }), 500


# ============================================================
# GET STUDENT NUDGE
# ============================================================

@app.route(
    "/student/nudge/<student_id>",
    methods=["GET"]
)
def get_student_nudge(student_id):

    with data_lock:

        student = students.get(student_id)

        if student is None:

            return jsonify({

                "status": "error",

                "message":
                    "Student not found"

            }), 404

        nudge = student.get("nudge")

        if not nudge:

            return jsonify({

                "status": "success",

                "has_nudge": False,

                "nudge": None

            })

        return jsonify({

            "status": "success",

            "has_nudge": True,

            "nudge": nudge

        })


# ============================================================
# MARK NUDGE AS READ
# ============================================================

@app.route(
    "/student/nudge/<student_id>/read",
    methods=["POST"]
)
def mark_nudge_read(student_id):

    with data_lock:

        student = students.get(student_id)

        if student is None:

            return jsonify({

                "status": "error",

                "message":
                    "Student not found"

            }), 404

        student["nudge"] = None

    return jsonify({

        "status": "success",

        "message":
            "Nudge marked as read"

    })


# ============================================================
# GET LIVE ATTENTION HISTORY
# ============================================================

@app.route(
    "/admin/history/<student_id>",
    methods=["GET"]
)
def get_history(student_id):

    history = []

    if not os.path.exists(LIVE_DATA_FILE):

        return jsonify({

            "status": "success",

            "student_id":
                student_id,

            "history": []

        })

    try:

        with open(
            LIVE_DATA_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                if str(
                    row.get(
                        "student_id",
                        ""
                    )
                ).strip() == student_id:

                    history.append(row)

        return jsonify({

            "status": "success",

            "student_id":
                student_id,

            "total_records":
                len(history),

            "history":
                history

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message":
                str(e)

        }), 500


# ============================================================
# ATTENTION TRANSITION ANALYSIS
# ============================================================

@app.route(
    "/admin/transitions/<student_id>",
    methods=["GET"]
)
def get_transitions(student_id):

    history = []

    if not os.path.exists(LIVE_DATA_FILE):

        return jsonify({

            "status": "success",

            "student_id":
                student_id,

            "total_transitions":
                0,

            "transitions": {}

        })

    try:

        with open(
            LIVE_DATA_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:

                if str(
                    row.get(
                        "student_id",
                        ""
                    )
                ).strip() == student_id:

                    status = str(
                        row.get(
                            "attention_status",
                            ""
                        )
                    ).strip().upper()

                    if status in [
                        "HIGH ATTENTION",
                        "MODERATE ATTENTION",
                        "LOW ATTENTION"
                    ]:

                        history.append(status)

        transition_counts = {}

        for previous, current in zip(
            history,
            history[1:]
        ):

            if previous != current:

                transition = (
                    previous
                    + " → "
                    + current
                )

                transition_counts[
                    transition
                ] = transition_counts.get(
                    transition,
                    0
                ) + 1

        total_transitions = sum(
            transition_counts.values()
        )

        return jsonify({

            "status": "success",

            "student_id":
                student_id,

            "total_transitions":
                total_transitions,

            "transitions":
                transition_counts

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message":
                str(e)

        }), 500


# ============================================================
# GET CURRENT ACTIVE STUDENT
# ============================================================

@app.route(
    "/student/active",
    methods=["GET"]
)
def get_active_student():

    with data_lock:

        if not students:

            return jsonify({

                "status": "success",

                "active": False,

                "student": None

            })

        active_student = max(

            students.values(),

            key=lambda student:
                student.get(
                    "joined_at",
                    ""
                )
        )

    return jsonify({

        "status": "success",

        "active": True,

        "student": {

            "student_id":
                active_student["student_id"],

            "student_name":
                active_student["student_name"],

            "email":
                active_student["email"]

        }

    })


# ============================================================
# GET ALL STUDENTS
# ============================================================

@app.route(
    "/admin/students",
    methods=["GET"]
)
def get_students():

    with data_lock:

        student_list = list(
            students.values()
        )

    return jsonify({

        "status": "success",

        "total_students":
            len(student_list),

        "students":
            student_list

    })


# ============================================================
# GET ONE STUDENT
# ============================================================

@app.route(
    "/admin/student/<student_id>",
    methods=["GET"]
)
def get_student(student_id):

    with data_lock:

        student = students.get(
            student_id
        )

    if student is None:

        return jsonify({

            "status": "error",

            "message":
                "Student not found"

        }), 404

    return jsonify({

        "status": "success",

        "student":
            student

    })


# ============================================================
# ADMIN DASHBOARD SUMMARY
# ============================================================

@app.route(
    "/admin/dashboard",
    methods=["GET"]
)
def dashboard():

    with data_lock:

        student_list = list(
            students.values()
        )

    total_students = len(
        student_list
    )

    if total_students == 0:

        return jsonify({

            "status": "success",

            "total_students": 0,

            "average_attention": 0,

            "high_attention": 0,

            "moderate_attention": 0,

            "low_attention": 0,

            "total_alerts": 0,

            "total_distractions": 0,

            "total_transitions": 0,

            "students": []

        })

    scores = [

        float(
            s.get(
                "attention_score",
                0
            )
        )

        for s in student_list

    ]

    average_attention = \
        sum(scores) / len(scores)

    high_attention = sum(

        1

        for s in student_list

        if str(
            s.get(
                "attention_status",
                ""
            )
        ).upper()
        == "HIGH ATTENTION"

    )

    moderate_attention = sum(

        1

        for s in student_list

        if str(
            s.get(
                "attention_status",
                ""
            )
        ).upper()
        == "MODERATE ATTENTION"

    )

    low_attention = sum(

        1

        for s in student_list

        if str(
            s.get(
                "attention_status",
                ""
            )
        ).upper()
        == "LOW ATTENTION"

    )

    total_alerts = sum(

        int(
            s.get(
                "alerts",
                0
            )
        )

        for s in student_list

    )

    total_distractions = sum(

        int(
            s.get(
                "distractions",
                0
            )
        )

        for s in student_list

    )

    total_transitions = sum(

        int(
            s.get(
                "transitions",
                0
            )
        )

        for s in student_list

    )

    return jsonify({

        "status": "success",

        "total_students":
            total_students,

        "average_attention":
            round(
                average_attention,
                2
            ),

        "high_attention":
            high_attention,

        "moderate_attention":
            moderate_attention,

        "low_attention":
            low_attention,

        "total_alerts":
            total_alerts,

        "total_distractions":
            total_distractions,

        "total_transitions":
            total_transitions,

        "students":
            student_list

    })


# ============================================================
# STUDENT LEAVES CLASS
# ============================================================

@app.route(
    "/student/leave",
    methods=["POST"]
)
def student_leave():

    try:

        data = request.get_json()

        student_id = str(
            data.get(
                "student_id",
                ""
            )
        ).strip()

        if not student_id:

            return jsonify({

                "status": "error",

                "message":
                    "student_id is required"

            }), 400

        with data_lock:

            if student_id in students:

                students[
                    student_id
                ]["attention_status"] = \
                    "LEFT CLASS"

                students[
                    student_id
                ]["last_update"] = \
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

        return jsonify({

            "status": "success",

            "message":
                "Student left the class"

        })

    except Exception as e:

        return jsonify({

            "status": "error",

            "message":
                str(e)

        }), 500


# ============================================================
# SERVER START
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print(" STUDENT ATTENTION LIVE SERVER")
    print("==========================================")
    print()

    print("Server running on:")

    print(
        f"http://localhost:{PORT}"
    )

    print()

    print("Available endpoints:")
    print()

    print("GET  /")
    print("POST /student/join")
    print("POST /student/update")
    print("POST /student/nudge")
    print("GET  /student/nudge/<student_id>")
    print("POST /student/nudge/<student_id>/read")
    print("POST /student/leave")
    print("GET  /admin/students")
    print("GET  /admin/student/<student_id>")
    print("GET  /admin/dashboard")
    print("GET  /admin/history/<student_id>")
    print("GET  /admin/transitions/<student_id>")

    print()

    print("Ready for multiple students.")

    print("==========================================")
    print()


    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )