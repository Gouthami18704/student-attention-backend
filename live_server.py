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

PORT = int(
    os.environ.get(
        "PORT",
        5000
    )
)


DATA_DIR = "WACV data"

LIVE_DATA_FILE = os.path.join(
    DATA_DIR,
    "live_student_data.csv"
)


os.makedirs(
    DATA_DIR,
    exist_ok=True
)


students = {}

data_lock = threading.Lock()


# ============================================================
# CSV INITIALIZATION
# ============================================================

def initialize_csv():

    if not os.path.exists(
        LIVE_DATA_FILE
    ):

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
                "alert_message",
                "recommendation",
                "distractions",
                "transitions",
                "stability",
                "face_detected",
                "looking_away"
            ])


initialize_csv()


# ============================================================
# HOME
# ============================================================

@app.route(
    "/",
    methods=["GET"]
)
def home():

    return jsonify({

        "status":
            "success",

        "message":
            "Student Attention Live Server is running",

        "server":
            "Flask",

        "port":
            PORT
    })


# ============================================================
# STUDENT JOIN
# ============================================================

@app.route(
    "/student/join",
    methods=["POST"]
)
def student_join():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "status":
                    "error",

                "message":
                    "No student data received"

            }), 400


        student_id = str(
            data.get(
                "student_id",
                ""
            )
        ).strip()


        student_name = str(
            data.get(
                "student_name",
                ""
            )
        ).strip()


        email = str(
            data.get(
                "email",
                ""
            )
        ).strip()


        if not student_id:

            return jsonify({

                "status":
                    "error",

                "message":
                    "student_id is required"

            }), 400


        if not student_name:

            return jsonify({

                "status":
                    "error",

                "message":
                    "student_name is required"

            }), 400


        if not email:

            return jsonify({

                "status":
                    "error",

                "message":
                    "email is required"

            }), 400


        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        student_data = {

            "student_id":
                student_id,

            "student_name":
                student_name,

            "email":
                email,

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

            "alert_message":
                "",

            "latest_alert":
                None,

            "alert_messages":
                [],

            "recommendation":
                "Waiting for attention analysis...",

            "distractions":
                0,

            "transitions":
                0,

            "stability":
                "UNKNOWN",

            "face_detected":
                True,

            "looking_away":
                False,

            "drowsiness_detected":
                False,

            "nudge":
                None,

            "joined_at":
                now,

            "last_update":
                now
        }


        with data_lock:

            students[
                student_id
            ] = student_data


        return jsonify({

            "status":
                "success",

            "message":
                "Student joined the online class",

            "student":
                student_data

        })


    except Exception as e:

        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# STUDENT UPDATE
# ============================================================

@app.route(
    "/student/update",
    methods=["POST"]
)
def student_update():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "status":
                    "error",

                "message":
                    "No attention data received"

            }), 400


        student_id = str(
            data.get(
                "student_id",
                ""
            )
        ).strip()


        if not student_id:

            return jsonify({

                "status":
                    "error",

                "message":
                    "student_id is required"

            }), 400


        now = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )


        with data_lock:

            # ------------------------------------------------
            # CREATE STUDENT IF NOT FOUND
            # ------------------------------------------------

            if student_id not in students:

                students[
                    student_id
                ] = {

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

                    "alert_message":
                        "",

                    "latest_alert":
                        None,

                    "alert_messages":
                        [],

                    "recommendation":
                        "Waiting for attention analysis...",

                    "distractions":
                        0,

                    "transitions":
                        0,

                    "stability":
                        "UNKNOWN",

                    "face_detected":
                        True,

                    "looking_away":
                        False,

                    "drowsiness_detected":
                        False,

                    "nudge":
                        None,

                    "joined_at":
                        now,

                    "last_update":
                        now
                }


            student = students[
                student_id
            ]


            # =================================================
            # BASIC INFORMATION
            # =================================================

            if "student_name" in data:

                student[
                    "student_name"
                ] = str(
                    data[
                        "student_name"
                    ]
                )


            if "email" in data:

                student[
                    "email"
                ] = str(
                    data[
                        "email"
                    ]
                )


            # =================================================
            # ATTENTION SCORE
            # =================================================

            if "attention_score" in data:

                student[
                    "attention_score"
                ] = float(
                    data[
                        "attention_score"
                    ]
                )


            # =================================================
            # ATTENTION STATUS
            # =================================================

            # Accept both names so older bridge versions
            # also continue working.

            if "attention_status" in data:

                student[
                    "attention_status"
                ] = str(
                    data[
                        "attention_status"
                    ]
                )

            elif "status" in data:

                student[
                    "attention_status"
                ] = str(
                    data[
                        "status"
                    ]
                )


            # =================================================
            # PREDICTED CLASS
            # =================================================

            if "predicted_class" in data:

                student[
                    "predicted_class"
                ] = int(
                    data[
                        "predicted_class"
                    ]
                )


            # =================================================
            # ALERTS
            # =================================================

            incoming_alerts = data.get(
                "alert_messages",
                []
            )


            if not isinstance(
                incoming_alerts,
                list
            ):

                incoming_alerts = []


            incoming_alerts = [

                str(alert).strip()

                for alert in incoming_alerts

                if str(alert).strip()
            ]


            latest_alert = data.get(
                "latest_alert",
                None
            )


            if latest_alert:

                latest_alert = str(
                    latest_alert
                ).strip()


            # ------------------------------------------------
            # Store the latest alert
            # ------------------------------------------------

            if latest_alert:

                student[
                    "latest_alert"
                ] = latest_alert

                student[
                    "alert_message"
                ] = latest_alert


            elif incoming_alerts:

                student[
                    "latest_alert"
                ] = incoming_alerts[-1]

                student[
                    "alert_message"
                ] = incoming_alerts[-1]


            # ------------------------------------------------
            # Store alert messages
            # ------------------------------------------------

            if incoming_alerts:

                existing_alerts = student.get(
                    "alert_messages",
                    []
                )

                if not isinstance(
                    existing_alerts,
                    list
                ):

                    existing_alerts = []


                for alert in incoming_alerts:

                    if alert not in existing_alerts:

                        existing_alerts.append(
                            alert
                        )


                # Keep only recent unique alert messages.
                student[
                    "alert_messages"
                ] = existing_alerts[-20:]


            # ------------------------------------------------
            # TOTAL ALERT COUNT
            # ------------------------------------------------

            if "alerts" in data:

                try:

                    incoming_alert_count = int(
                        data[
                            "alerts"
                        ]
                    )

                except Exception:

                    incoming_alert_count = 0

            else:

                incoming_alert_count = 0


            # Do not reduce the existing total accidentally.
            student[
                "alerts"
            ] = max(
                int(
                    student.get(
                        "alerts",
                        0
                    )
                ),
                incoming_alert_count
            )


            # =================================================
            # RECOMMENDATION
            # =================================================

            if "recommendation" in data:

                student[
                    "recommendation"
                ] = str(
                    data[
                        "recommendation"
                    ]
                )


            # =================================================
            # ANALYTICS
            # =================================================

            if "distractions" in data:

                student[
                    "distractions"
                ] = int(
                    data[
                        "distractions"
                    ]
                )


            if "transitions" in data:

                student[
                    "transitions"
                ] = int(
                    data[
                        "transitions"
                    ]
                )


            if "stability" in data:

                student[
                    "stability"
                ] = str(
                    data[
                        "stability"
                    ]
                )


            # =================================================
            # CAMERA / GAZE
            # =================================================

            if "face_detected" in data:

                student[
                    "face_detected"
                ] = bool(
                    data[
                        "face_detected"
                    ]
                )


            if "looking_away" in data:

                student[
                    "looking_away"
                ] = bool(
                    data[
                        "looking_away"
                    ]
                )


            if "drowsiness_detected" in data:

                student[
                    "drowsiness_detected"
                ] = bool(
                    data[
                        "drowsiness_detected"
                    ]
                )


            # =================================================
            # LAST UPDATE
            # =================================================

            student[
                "last_update"
            ] = now


            # =================================================
            # CSV
            # =================================================

            with open(
                LIVE_DATA_FILE,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                writer = csv.writer(file)

                writer.writerow([

                    student[
                        "last_update"
                    ],

                    student[
                        "student_id"
                    ],

                    student[
                        "student_name"
                    ],

                    student[
                        "email"
                    ],

                    student[
                        "attention_score"
                    ],

                    student[
                        "attention_status"
                    ],

                    student[
                        "predicted_class"
                    ],

                    student[
                        "attendance"
                    ],

                    student[
                        "alerts"
                    ],

                    student[
                        "alert_message"
                    ],

                    student[
                        "recommendation"
                    ],

                    student[
                        "distractions"
                    ],

                    student[
                        "transitions"
                    ],

                    student[
                        "stability"
                    ],

                    student[
                        "face_detected"
                    ],

                    student[
                        "looking_away"
                    ]
                ])


        return jsonify({

            "status":
                "success",

            "message":
                "Attention data updated",

            "student":
                student

        })


    except Exception as e:

        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# NUDGE
# ============================================================

@app.route(
    "/student/nudge",
    methods=["POST"]
)
def student_nudge():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "status":
                    "error",

                "message":
                    "No nudge data received"

            }), 400


        student_id = str(
            data.get(
                "student_id",
                ""
            )
        ).strip()


        if not student_id:

            return jsonify({

                "status":
                    "error",

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

                    "status":
                        "error",

                    "message":
                        "Student not found"

                }), 404


            students[
                student_id
            ][
                "nudge"
            ] = {

                "message":
                    message,

                "timestamp":
                    datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),

                "read":
                    False
            }


        return jsonify({

            "status":
                "success",

            "message":
                "Nudge sent successfully"

        })


    except Exception as e:

        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# GET NUDGE
# ============================================================

@app.route(
    "/student/nudge/<student_id>",
    methods=["GET"]
)
def get_student_nudge(student_id):

    with data_lock:

        student = students.get(
            student_id
        )


        if student is None:

            return jsonify({

                "status":
                    "error",

                "message":
                    "Student not found"

            }), 404


        nudge = student.get(
            "nudge"
        )


        if not nudge:

            return jsonify({

                "status":
                    "success",

                "has_nudge":
                    False,

                "nudge":
                    None

            })


        return jsonify({

            "status":
                "success",

            "has_nudge":
                True,

            "nudge":
                nudge

        })


# ============================================================
# MARK NUDGE READ
# ============================================================

@app.route(
    "/student/nudge/<student_id>/read",
    methods=["POST"]
)
def mark_nudge_read(student_id):

    with data_lock:

        student = students.get(
            student_id
        )


        if student is None:

            return jsonify({

                "status":
                    "error",

                "message":
                    "Student not found"

            }), 404


        student[
            "nudge"
        ] = None


    return jsonify({

        "status":
            "success",

        "message":
            "Nudge marked as read"

    })


# ============================================================
# HISTORY
# ============================================================

@app.route(
    "/admin/history/<student_id>",
    methods=["GET"]
)
def get_history(student_id):

    history = []


    if not os.path.exists(
        LIVE_DATA_FILE
    ):

        return jsonify({

            "status":
                "success",

            "student_id":
                student_id,

            "history":
                []

        })


    try:

        with open(
            LIVE_DATA_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(
                file
            )


            for row in reader:

                if str(
                    row.get(
                        "student_id",
                        ""
                    )
                ).strip() == student_id:

                    history.append(
                        row
                    )


        return jsonify({

            "status":
                "success",

            "student_id":
                student_id,

            "total_records":
                len(history),

            "history":
                history

        })


    except Exception as e:

        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# TRANSITIONS
# ============================================================

@app.route(
    "/admin/transitions/<student_id>",
    methods=["GET"]
)
def get_transitions(student_id):

    history = []


    if not os.path.exists(
        LIVE_DATA_FILE
    ):

        return jsonify({

            "status":
                "success",

            "student_id":
                student_id,

            "total_transitions":
                0,

            "transitions":
                {}

        })


    try:

        with open(
            LIVE_DATA_FILE,
            "r",
            newline="",
            encoding="utf-8"
        ) as file:

            reader = csv.DictReader(
                file
            )


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

                        "LOW ATTENTION",

                        "ATTENTIVE",

                        "PARTLY ENGAGED"

                    ]:

                        history.append(
                            status
                        )


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
                ] = (
                    transition_counts.get(
                        transition,
                        0
                    )
                    + 1
                )


        return jsonify({

            "status":
                "success",

            "student_id":
                student_id,

            "total_transitions":
                sum(
                    transition_counts.values()
                ),

            "transitions":
                transition_counts

        })


    except Exception as e:

        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# ACTIVE STUDENT
# ============================================================

@app.route(
    "/student/active",
    methods=["GET"]
)
def get_active_student():

    with data_lock:

        if not students:

            return jsonify({

                "status":
                    "success",

                "active":
                    False,

                "student":
                    None

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

        "status":
            "success",

        "active":
            True,

        "student": {

            "student_id":
                active_student[
                    "student_id"
                ],

            "student_name":
                active_student[
                    "student_name"
                ],

            "email":
                active_student[
                    "email"
                ]
        }

    })


# ============================================================
# ALL STUDENTS
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

        "status":
            "success",

        "total_students":
            len(student_list),

        "students":
            student_list

    })


# ============================================================
# ONE STUDENT
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

            "status":
                "error",

            "message":
                "Student not found"

        }), 404


    return jsonify({

        "status":
            "success",

        "student":
            student

    })


# ============================================================
# ADMIN DASHBOARD
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

            "status":
                "success",

            "total_students":
                0,

            "average_attention":
                0,

            "high_attention":
                0,

            "moderate_attention":
                0,

            "low_attention":
                0,

            "total_alerts":
                0,

            "total_distractions":
                0,

            "total_transitions":
                0,

            "students":
                []

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


    average_attention = (
        sum(scores)
        /
        len(scores)
    )


    high_attention = sum(

        1

        for s in student_list

        if str(
            s.get(
                "attention_status",
                ""
            )
        ).upper()
        in [
            "HIGH ATTENTION",
            "ATTENTIVE"
        ]

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
        in [
            "MODERATE ATTENTION",
            "PARTLY ENGAGED"
        ]

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

    ]


    total_distractions = sum(

        int(
            s.get(
                "distractions",
                0
            )
        )

        for s in student_list

    ]


    total_transitions = sum(

        int(
            s.get(
                "transitions",
                0
            )
        )

        for s in student_list

    ]


    return jsonify({

        "status":
            "success",

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
# STUDENT LEAVE
# ============================================================

@app.route(
    "/student/leave",
    methods=["POST"]
)
def student_leave():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "status":
                    "error",

                "message":
                    "No student data received"

            }), 400


        student_id = str(
            data.get(
                "student_id",
                ""
            )
        ).strip()


        if not student_id:

            return jsonify({

                "status":
                    "error",

                "message":
                    "student_id is required"

            }), 400


        with data_lock:

            if student_id in students:

                students[
                    student_id
                ][
                    "attention_status"
                ] = "LEFT CLASS"


                students[
                    student_id
                ][
                    "last_update"
                ] = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )


        return jsonify({

            "status":
                "success",

            "message":
                "Student left the class"

        })


    except Exception as e:

        return jsonify({

            "status":
                "error",

            "message":
                str(e)

        }), 500


# ============================================================
# SERVER
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print(" STUDENT ATTENTION LIVE SERVER")
    print("==========================================")
    print()

    print(
        f"Server running on port {PORT}"
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
    print("GET  /student/active")
    print("GET  /admin/students")
    print("GET  /admin/student/<student_id>")
    print("GET  /admin/dashboard")
    print("GET  /admin/history/<student_id>")
    print("GET  /admin/transitions/<student_id>")
    print()

    print(
        "Ready for multiple students."
    )

    print(
        "=========================================="
    )

    app.run(
        host=HOST,
        port=PORT,
        debug=False,
        threaded=True
    )