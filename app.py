from flask import Flask, jsonify, request, send_from_directory, redirect, session
from flask_cors import CORS
from datetime import datetime
import sqlite3
import subprocess
import os
import json
import tempfile

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "Frontend")
HTML_DIR     = os.path.join(FRONTEND_DIR, "HTML")
app = Flask(__name__, static_folder=None)
app.secret_key = "gehuconnect_super_secret_key"
CORS(app)

@app.before_request
def security_check():
    if request.path == "/admin.html" and not session.get("admin_logged_in"):
        return redirect("/admin_login.html")


DB_PATH      = os.path.join(os.path.dirname(__file__), "gehuconnect.db")
BACKEND_DIR  = os.path.join(os.path.dirname(__file__), "Backend")


# ──────────────────────────────────────────────────────────────
#  DATABASE INITIALISATION
# ──────────────────────────────────────────────────────────────
def init_db():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id       TEXT PRIMARY KEY,
            name     TEXT,
            branch   TEXT,
            cgpa     REAL,
            hostel   TEXT,
            room     TEXT,
            phone    TEXT,
            password TEXT
        );

        CREATE TABLE IF NOT EXISTS attendance (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject    TEXT,
            percentage REAL
        );

        CREATE TABLE IF NOT EXISTS notices (
            id       INTEGER PRIMARY KEY,
            title    TEXT,
            category TEXT,
            date     TEXT,
            urgency  TEXT
        );

        CREATE TABLE IF NOT EXISTS assignments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            subject    TEXT,
            title      TEXT,
            due_date   TEXT
        );

        CREATE TABLE IF NOT EXISTS admins (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        );

        CREATE TABLE IF NOT EXISTS pending_admissions (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name        TEXT,
            dob              TEXT,
            gender           TEXT,
            personal_email   TEXT,
            phone            TEXT,
            location         TEXT,
            tenth_pct        REAL,
            twelfth_pct      REAL,
            preferred_branch TEXT,
            hostel_required  TEXT,
            status           TEXT DEFAULT 'pending',
            submitted_at     TEXT
        );

        CREATE TABLE IF NOT EXISTS clubs (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT,
            description TEXT,
            category    TEXT,
            capacity    INTEGER,
            enrolled    INTEGER DEFAULT 0,
            coordinator TEXT
        );
    """)

    # ── Migrate: add password column if it doesn't exist yet ──
    try:
        cur.execute("ALTER TABLE students ADD COLUMN password TEXT")
    except Exception:
        pass  # column already present

    # ── Seed: students ─────────────────────────────────────────
    if cur.execute("SELECT COUNT(*) FROM students").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO students (id,name,branch,cgpa,hostel,room,phone,password) VALUES (?,?,?,?,?,?,?,?)",
            [
                ("2419260","Mohit Purohit",  "CSE",8.2,"Block C","214","9876543210","2419260"),
                ("2418628","Maitri Goyal",   "CSE",8.0,"Block A","105","9876543211","2418628"),
                ("2419475","Manisha Bisht",  "CSE",7.8,"Block B","302","9876543212","2419475"),
                ("2418996","Shyamali Bisht", "CSE",7.5,"Block D","410","9876543213","2418996"),
            ]
        )
    else:
        # Ensure existing students have a default password (= their id)
        cur.execute("UPDATE students SET password = id WHERE password IS NULL OR password = ''")

    # ── Seed: attendance ───────────────────────────────────────
    if cur.execute("SELECT COUNT(*) FROM attendance").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO attendance(student_id,subject,percentage) VALUES (?,?,?)",
            [
                ("2419260","Maths",    78),
                ("2419260","Physics",  45),
                ("2419260","Chemistry",62),
                ("2419260","DSA",      85),
                ("2419260","English",  71),
                ("2418628","Maths",    80),
                ("2418628","Physics",  74),
                ("2418628","Chemistry",55),
                ("2419475","Maths",    90),
                ("2419475","DSA",      88),
                ("2418996","Maths",    65),
                ("2418996","Physics",  72),
            ]
        )

    # ── Seed: notices ──────────────────────────────────────────
    if cur.execute("SELECT COUNT(*) FROM notices").fetchone()[0] == 0:
        cur.executemany("INSERT INTO notices VALUES (?,?,?,?,?)", [
            (1,"Fee submission last date extended","Fee",     "2026-05-30","urgent"),
            (2,"Workshop on AI this Friday",       "Event",   "2026-05-28","normal"),
            (3,"End-semester exam schedule released","Exam",  "2026-05-25","urgent"),
            (4,"Library extended hours during exams","Academic","2026-05-24","normal"),
            (5,"Annual Sports Day registrations open","Event","2026-06-05","normal"),
            (6,"Scholarship form deadline approaching","Fee", "2026-06-01","urgent"),
        ])

    # ── Seed: assignments ──────────────────────────────────────
    if cur.execute("SELECT COUNT(*) FROM assignments").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO assignments(student_id,subject,title,due_date) VALUES (?,?,?,?)",
            [
                ("2419260","Maths",   "Integration assignment",  "2026-06-05"),
                ("2419260","DSA",     "Graph problems",          "2026-05-30"),
                ("2419260","Physics", "Optics lab report",       "2026-06-10"),
                ("2418628","Maths",   "Calculus sheet",          "2026-06-03"),
                ("2419475","DSA",     "Sorting algorithms",      "2026-06-01"),
            ]
        )

    # ── Seed: admins ───────────────────────────────────────────
    if cur.execute("SELECT COUNT(*) FROM admins").fetchone()[0] == 0:
        cur.execute("INSERT INTO admins (username,password) VALUES (?,?)", ("admin","admin123"))

    # ── Seed: clubs ────────────────────────────────────────────
    if cur.execute("SELECT COUNT(*) FROM clubs").fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO clubs (name,description,category,capacity,enrolled,coordinator) VALUES (?,?,?,?,?,?)",
            [
                ("Coding Club",     "Competitive programming & open-source contributions","Technical",50,42,"Prof. Sharma"),
                ("Robotics Society","Hardware projects, Arduino, and drone technology",   "Technical",30,28,"Prof. Kumar"),
                ("Photography Club","Photography, videography & visual storytelling",      "Creative", 40,35,"Prof. Verma"),
                ("NSS",             "National Service Scheme — community outreach & seva","Social",   100,67,"Prof. Singh"),
                ("Debate Society",  "Parliamentary debates and public speaking training", "Cultural", 60,45,"Prof. Gupta"),
                ("Music Club",      "Classical and contemporary music performances",       "Cultural", 35,35,"Prof. Rao"),
                ("E-Sports Club",   "Competitive gaming and esports tournament team",      "Sports",   50,30,"Prof. Joshi"),
                ("AI Research Group","Machine learning projects, papers & research",      "Technical",25,10,"Prof. Mishra"),
            ]
        )

    con.commit()
    con.close()


# ──────────────────────────────────────────────────────────────
#  C++ PIPELINE HELPER
# ──────────────────────────────────────────────────────────────
def run_cpp(cpp_file, input_data):
    exe = cpp_file.replace(".cpp", ".exe")
    if not os.path.exists(exe) or os.path.getmtime(cpp_file) > os.path.getmtime(exe):
        result = subprocess.run(
            ["g++", cpp_file, "-o", exe],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            return {"error": "compile failed", "detail": result.stderr}

    fd, temp_path = tempfile.mkstemp(suffix=".txt", dir=BACKEND_DIR, text=True)
    with os.fdopen(fd, 'w') as f:
        f.write(input_data)

    result = subprocess.run([exe, temp_path], capture_output=True, text=True, cwd=BACKEND_DIR)
    try:
        os.remove(temp_path)
    except Exception:
        pass

    if result.returncode != 0:
        return {"error": "runtime error", "detail": result.stderr}

    try:
        return json.loads(result.stdout)
    except Exception:
        return {"error": "bad JSON output", "raw": result.stdout}


# ──────────────────────────────────────────────────────────────
#  STUDENT ROUTES
# ──────────────────────────────────────────────────────────────
@app.route("/login")
def login():
    student_id = request.args.get("id", "")
    password   = request.args.get("password", "")

    con = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT id,name,branch,cgpa,hostel,room,phone,password FROM students").fetchall()
    con.close()

    # Find student — if password provided, also validate it; else just check ID
    matched = None
    for r in rows:
        if r[0] == student_id:
            if password == "" or r[7] == password or r[7] is None:
                matched = r
                break

    if not matched:
        return jsonify({"error": "Student not found or wrong password"}), 404

    input_data  = student_id + "\n"
    input_data += "\n".join(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{r[6]}" for r in rows) + "\n"
    cpp_path = os.path.join(BACKEND_DIR, "login.cpp")
    result   = run_cpp(cpp_path, input_data)
    return jsonify(result)


@app.route("/attendance")
def attendance():
    student_id = request.args.get("id", "")
    con  = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT subject,percentage FROM attendance WHERE student_id=?", (student_id,)
    ).fetchall()
    con.close()

    if not rows:
        return jsonify({"error": "No attendance data"}), 404

    input_data = "\n".join(f"{r[0]},{r[1]}" for r in rows) + "\n"
    cpp_path   = os.path.join(BACKEND_DIR, "attendance.cpp")
    result     = run_cpp(cpp_path, input_data)
    return jsonify(result)


@app.route("/notices")
def notices():
    category = request.args.get("category", "all")
    con  = sqlite3.connect(DB_PATH)
    rows = con.execute("SELECT id,title,category,date,urgency FROM notices").fetchall()
    con.close()

    input_data = category + "\n"
    input_data += "\n".join(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}" for r in rows) + "\n"
    cpp_path   = os.path.join(BACKEND_DIR, "notices.cpp")
    result     = run_cpp(cpp_path, input_data)
    return jsonify(result)


@app.route("/assignments")
def assignments():
    student_id = request.args.get("id", "")
    con  = sqlite3.connect(DB_PATH)
    rows = con.execute(
        "SELECT subject,title,due_date FROM assignments WHERE student_id=?", (student_id,)
    ).fetchall()
    con.close()

    if not rows:
        return jsonify({"error": "No assignments"}), 404

    input_data = "\n".join(f"{r[0]},{r[1]},{r[2]}" for r in rows) + "\n"
    cpp_path   = os.path.join(BACKEND_DIR, "assignments.cpp")
    result     = run_cpp(cpp_path, input_data)
    return jsonify(result)


# ──────────────────────────────────────────────────────────────
#  CLUBS ROUTE (Phase 3 — pure Python/SQLite, no C++ pipeline)
# ──────────────────────────────────────────────────────────────
@app.route("/clubs")
def clubs():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute("SELECT * FROM clubs ORDER BY name").fetchall()
    con.close()

    result = []
    for r in rows:
        enrolled = r["enrolled"]
        capacity = r["capacity"]
        pct = enrolled / capacity if capacity > 0 else 1
        if pct >= 1.0:
            status = "full"
        elif pct >= 0.8:
            status = "limited"
        else:
            status = "open"
        result.append({
            "id":          r["id"],
            "name":        r["name"],
            "description": r["description"],
            "category":    r["category"],
            "capacity":    capacity,
            "enrolled":    enrolled,
            "spots_left":  max(0, capacity - enrolled),
            "coordinator": r["coordinator"],
            "status":      status
        })
    return jsonify(result)


# ──────────────────────────────────────────────────────────────
#  ADMISSION FORM ROUTES (Phase 3)
# ──────────────────────────────────────────────────────────────
@app.route("/submit_admission", methods=["POST"])
def submit_admission():
    """Public route — students submit their admission application."""
    data = request.json
    required = ["full_name","dob","gender","personal_email","phone",
                "location","tenth_pct","twelfth_pct","preferred_branch","hostel_required"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"Missing field: {field}"}), 400
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute("""
            INSERT INTO pending_admissions
                (full_name,dob,gender,personal_email,phone,location,
                 tenth_pct,twelfth_pct,preferred_branch,hostel_required,submitted_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data["full_name"], data["dob"], data["gender"],
            data["personal_email"], data["phone"], data["location"],
            float(data["tenth_pct"]), float(data["twelfth_pct"]),
            data["preferred_branch"], data["hostel_required"],
            datetime.now().strftime("%Y-%m-%d %H:%M")
        ))
        app_id = cur.lastrowid
        con.commit()
        con.close()
        return jsonify({"success": True, "application_id": app_id,
                        "message": "Application submitted! The admin will review and assign your credentials."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload_csv_bulk", methods=["POST"])
def upload_csv_bulk():
    """Admin only — upload multiple CSV files and import records in bulk."""
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    if "files" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    uploaded_files = request.files.getlist("files")
    if not uploaded_files or uploaded_files[0].filename == '':
        return jsonify({"error": "No files selected"}), 400

    import csv
    import io

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    imported_count = 0
    errors = []

    for file in uploaded_files:
        if not file.filename.endswith('.csv'):
            continue
        try:
            # Read CSV content
            stream = io.StringIO(file.stream.read().decode("utf-8"), newline="")
            csv_reader = csv.DictReader(stream)
            for row in csv_reader:
                cleaned_row = {k.strip().lower() if k else "": v.strip() if v else "" for k, v in row.items()}
                
                # Retrieve fields with flexible header matching
                full_name = cleaned_row.get("full_name") or cleaned_row.get("name")
                dob = cleaned_row.get("dob") or cleaned_row.get("date of birth")
                gender = cleaned_row.get("gender")
                personal_email = cleaned_row.get("personal_email") or cleaned_row.get("email")
                phone = cleaned_row.get("phone") or cleaned_row.get("phone number")
                location = cleaned_row.get("location") or cleaned_row.get("address")
                
                try:
                    tenth_pct = float(cleaned_row.get("tenth_pct") or cleaned_row.get("10th%") or 0.0)
                except ValueError:
                    tenth_pct = 0.0
                try:
                    twelfth_pct = float(cleaned_row.get("twelfth_pct") or cleaned_row.get("12th%") or 0.0)
                except ValueError:
                    twelfth_pct = 0.0
                
                preferred_branch = cleaned_row.get("preferred_branch") or cleaned_row.get("branch")
                hostel_required = cleaned_row.get("hostel_required") or cleaned_row.get("hostel")
                
                if not full_name or not personal_email:
                    continue

                # Deduplicate based on email to prevent importing duplicate mock profiles
                existing = cur.execute(
                    "SELECT id FROM pending_admissions WHERE personal_email=?", (personal_email,)
                ).fetchone()
                if existing:
                    continue

                cur.execute("""
                    INSERT INTO pending_admissions
                        (full_name, dob, gender, personal_email, phone, location,
                         tenth_pct, twelfth_pct, preferred_branch, hostel_required, status, submitted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
                """, (
                    full_name, dob, gender, personal_email, phone, location,
                    tenth_pct, twelfth_pct, preferred_branch, hostel_required,
                    datetime.now().strftime("%Y-%m-%d %H:%M")
                ))
                imported_count += 1
        except Exception as e:
            errors.append(f"Error parsing {file.filename}: {str(e)}")

    con.commit()
    con.close()

    if errors and imported_count == 0:
        return jsonify({"error": "Failed to parse files.", "details": errors}), 400

    return jsonify({
        "success": True, 
        "message": f"Successfully imported {imported_count} student applications!",
        "imported": imported_count,
        "errors": errors
    })


@app.route("/api/pending_admissions", methods=["GET"])
def pending_admissions():
    """Admin only — list all pending applications."""
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    rows = con.execute(
        "SELECT * FROM pending_admissions ORDER BY submitted_at DESC"
    ).fetchall()
    con.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/approve_admissions", methods=["POST"])
def approve_admissions():
    """Admin only — approve selected pending applications and auto-generate credentials."""
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    ids  = data.get("ids", [])
    if not ids:
        return jsonify({"error": "No IDs provided"}), 400

    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    approved = []

    year_short = datetime.now().year % 100   # e.g. 26

    for pid in ids:
        row = cur.execute(
            "SELECT * FROM pending_admissions WHERE id=? AND status='pending'", (pid,)
        ).fetchone()
        if not row:
            continue

        # Column order: id,full_name,dob,gender,personal_email,phone,location,
        #               tenth_pct,twelfth_pct,preferred_branch,hostel_required,status,submitted_at
        full_name   = row[1]
        gender      = row[3]
        phone       = row[5]
        branch      = row[9]   # preferred_branch
        hostel_req  = row[10]  # hostel_required

        # ── Auto-generate Roll Number ──────────────────────────
        total_students = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
        serial = total_students + 1
        roll   = f"20{year_short:02d}{serial:04d}"   # e.g. 2026001

        # ── Auto-assign Section (based on branch headcount) ───
        count_in_branch = cur.execute(
            "SELECT COUNT(*) FROM students WHERE branch=?", (branch,)
        ).fetchone()[0]
        if   count_in_branch < 60:  section = "A"
        elif count_in_branch < 120: section = "B"
        else:                       section = "C"

        # ── Auto-assign Hostel + Room ──────────────────────────
        hostel_map = {"Female": "Block A", "Male": "Block C", "Other": "Block B"}
        hostel = hostel_map.get(gender, "Block C") if hostel_req == "Yes" else "Day Scholar"
        room   = str(100 + serial) if hostel_req == "Yes" else "—"

        # ── College Email & Default Password ──────────────────
        college_email = f"{roll}@gehu.ac.in"
        password      = roll   # default password = roll number

        # ── Insert into students table ────────────────────────
        cur.execute(
            "INSERT INTO students (id,name,branch,cgpa,hostel,room,phone,password) VALUES (?,?,?,?,?,?,?,?)",
            (roll, full_name, branch, 0.0, hostel, room, phone, password)
        )

        # ── Mark application as approved ──────────────────────
        cur.execute("UPDATE pending_admissions SET status='approved' WHERE id=?", (pid,))

        approved.append({
            "name":          full_name,
            "roll":          roll,
            "college_email": college_email,
            "password":      password,
            "branch":        branch,
            "section":       section,
            "hostel":        hostel,
            "room":          room
        })

    con.commit()
    con.close()
    return jsonify({"success": True, "approved": approved, "count": len(approved)})


# ──────────────────────────────────────────────────────────────
#  ADMIN ROUTES
# ──────────────────────────────────────────────────────────────
@app.route("/api/admin_login", methods=["POST"])
def admin_login():
    data     = request.json
    username = data.get("username")
    password = data.get("password")
    con = sqlite3.connect(DB_PATH)
    admin = con.execute(
        "SELECT * FROM admins WHERE username=? AND password=?", (username, password)
    ).fetchone()
    con.close()
    if admin:
        session["admin_logged_in"] = True
        return jsonify({"success": True})
    return jsonify({"error": "Invalid username or password"}), 401


@app.route("/api/admin_logout", methods=["POST"])
def admin_logout():
    session.pop("admin_logged_in", None)
    return jsonify({"success": True})


@app.route("/add_student", methods=["POST"])
def add_student():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO students (id,name,branch,cgpa,hostel,room,phone,password) VALUES (?,?,?,?,?,?,?,?)",
            (data["id"], data["name"], data["branch"], data["cgpa"],
             data["hostel"], data["room"], data["phone"],
             data.get("password", data["id"]))   # default password = id
        )
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Student added successfully!"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add_attendance", methods=["POST"])
def add_attendance():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO attendance (student_id,subject,percentage) VALUES (?,?,?)",
            (data["student_id"], data["subject"], data["percentage"])
        )
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Attendance recorded!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add_notice", methods=["POST"])
def add_notice():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO notices (title,category,date,urgency) VALUES (?,?,?,?)",
            (data["title"], data["category"], data["date"], data["urgency"])
        )
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Notice published!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/add_assignment", methods=["POST"])
def add_assignment():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO assignments (student_id,subject,title,due_date) VALUES (?,?,?,?)",
            (data["student_id"], data["subject"], data["title"], data["due_date"])
        )
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Assignment created!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_student_full", methods=["GET"])
def get_student_full():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    student_id = request.args.get("id")
    if not student_id:
        return jsonify({"error": "Missing student ID"}), 400
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    student     = cur.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    if not student:
        con.close()
        return jsonify({"error": "Student not found"}), 404
    attendance  = cur.execute("SELECT id,subject,percentage FROM attendance WHERE student_id=?",  (student_id,)).fetchall()
    assignments = cur.execute("SELECT id,subject,title,due_date FROM assignments WHERE student_id=?", (student_id,)).fetchall()
    con.close()
    return jsonify({
        "student":     dict(student),
        "attendance":  [dict(a) for a in attendance],
        "assignments": [dict(a) for a in assignments]
    })


@app.route("/api/update_student", methods=["POST"])
def update_student():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        old_id = data.get("old_id", data["id"])
        new_id = data["id"]
        cur.execute("""
            UPDATE students
            SET id=?, name=?, branch=?, cgpa=?, hostel=?, room=?, phone=?
            WHERE id=?
        """, (new_id, data["name"], data["branch"], data["cgpa"],
              data["hostel"], data["room"], data["phone"], old_id))
        if old_id != new_id:
            cur.execute("UPDATE attendance  SET student_id=? WHERE student_id=?", (new_id, old_id))
            cur.execute("UPDATE assignments SET student_id=? WHERE student_id=?", (new_id, old_id))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Student profile updated!"})
    except sqlite3.IntegrityError:
        return jsonify({"error": "Student ID already exists"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/delete_record", methods=["POST"])
def delete_record():
    if not session.get("admin_logged_in"):
        return jsonify({"error": "Unauthorized"}), 401
    data      = request.json
    table     = data.get("table")
    record_id = data.get("id")
    if table not in ["attendance", "assignments"]:
        return jsonify({"error": "Invalid table"}), 400
    try:
        con = sqlite3.connect(DB_PATH)
        cur = con.cursor()
        cur.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
        con.commit()
        con.close()
        return jsonify({"success": True, "message": "Record deleted!"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ──────────────────────────────────────────────────────────────
#  STATIC ROUTING
# ──────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return redirect("/index.html")

@app.route("/admin")
def admin_redirect():
    return redirect("/admin.html")

@app.route("/<path:filename>")
def serve_static(filename):
    if filename == "admin.html" and not session.get("admin_logged_in"):
        return redirect("/admin_login.html")
    # CSS, JS, and other assets are served from Frontend/ directly
    # HTML files are in Frontend/HTML/
    if filename.endswith(".html"):
        return send_from_directory(HTML_DIR, filename)
    return send_from_directory(FRONTEND_DIR, filename)


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
