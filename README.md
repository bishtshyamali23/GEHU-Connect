# GehuConnect — DAA Project (Phase 3 Complete)

> A full-stack student ERP portal for **Graphic Era Hill University (GEHU)** that demonstrates core **Data Structures & Algorithms** concepts through a live, production-grade academic management system.

---

## 👥 Team Members

| Member | Roll No | Module | DSA Concept |
|---|---|---|---|
| Maitri Goyal *(Lead)* | 2418628 | Login & Authentication | HashMap (`unordered_map`) |
| Mohit Chandra Purohit | 2419260 | Attendance Tracker + Predictor | Merge Sort |
| Manisha Bisht | 2419475 | Assignments Deadline Manager | Min-Heap (`extractMin`, `editDueDate`) |
| Shyamali Bisht | 2418996 | Notices Board + Auto-complete | Trie (DFS traversal) |

---

## 🗂️ Project Structure

```
GehuConnect--DAA-/
├── app.py                           # Flask server — REST API, SQLite, C++ pipeline, admin auth
├── gehuconnect.db                   # SQLite database (auto-created and seeded on first run)
├── generate_dummy_csv.py            # Script to generate 100 dummy student CSV files
├── dummy_students/                  # 100 individual student CSV files for bulk enrollment demo
│   ├── student_001.csv
│   ├── student_002.csv
│   └── ... (100 files total)
├── .gitignore
├── README.md
│
├── Frontend/
│   ├── CSS/
│   │   └── global.css               # Dark glassmorphism design system — all shared tokens & utilities
│   └── HTML/
│       ├── index.html               # Student login page (ID + Password)
│       ├── student_dashboard.html   # Stat cards — CGPA, Hostel, Room, Branch, upcoming deadlines
│       ├── attendance.html          # Subject attendance bars + Phase 3 predictor
│       ├── assignments.html         # Deadline-sorted assignment cards with countdown timers
│       ├── notices.html             # Notice board with category pill filter
│       ├── clubs.html               # Club directory with enrollment status
│       ├── admission_form.html      # Public new-student admission form
│       ├── admin.html               # Admin dashboard (protected, session-gated)
│       └── admin_login.html         # Admin login page
│
└── Backend/                         # C++ DSA modules (compiled at runtime via g++)
    ├── login.cpp                    # HashMap O(1) student lookup
    ├── attendance.cpp               # Merge Sort + Attendance Predictor
    ├── notices.cpp                  # Trie exact-match + DFS auto-complete
    └── assignments.cpp              # Min-Heap priority queue + editDueDate
```

---

## ✅ Phase 3 Deliverables — All Complete

### 🔧 Backend — Flask + SQLite (`app.py`)

The backend is a Python Flask server serving both the REST API and all static files.

**Architecture:** `Browser → Flask REST API → SQLite DB → C++ DSA binary → JSON response → Browser`

#### Database Tables

| Table | Purpose |
|---|---|
| `students` | Enrolled students (ID, name, branch, CGPA, hostel, room, phone, password) |
| `attendance` | Subject-wise attendance records per student |
| `assignments` | Assignment records with due dates per student |
| `notices` | University-wide announcements with category & urgency |
| `clubs` | Club directory with capacity, enrollment, and coordinator |
| `pending_admissions` | Incoming applications awaiting admin approval |
| `admins` | Admin credentials for the protected dashboard |

#### REST API Reference

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/login?id=ROLL&password=PASS` | — | Student login via HashMap lookup |
| `GET` | `/attendance?id=ROLL` | — | Attendance data sorted via Merge Sort |
| `GET` | `/notices?category=all\|Fee\|Event\|Exam\|Academic` | — | Filtered notices via Trie search |
| `GET` | `/assignments?id=ROLL` | — | Assignments sorted by deadline via Min-Heap |
| `GET` | `/clubs` | — | All clubs with status (open / limited / full) |
| `POST` | `/submit_admission` | — | Submit a new student admission application |
| `POST` | `/api/admin_login` | — | Admin login (creates server-side session) |
| `POST` | `/api/admin_logout` | Admin | Destroy admin session |
| `GET` | `/api/pending_admissions` | Admin | List all pending + approved applications |
| `POST` | `/api/approve_admissions` | Admin | Bulk-approve applications, auto-generate credentials |
| `POST` | `/api/upload_csv_bulk` | Admin | Upload multiple CSV files to bulk-import applicants |
| `POST` | `/add_student` | Admin | Manually add a single student |
| `POST` | `/add_attendance` | Admin | Record attendance for a student |
| `POST` | `/add_notice` | Admin | Publish a new notice |
| `POST` | `/add_assignment` | Admin | Create a new assignment for a student |
| `GET` | `/api/get_student_full?id=ROLL` | Admin | Fetch full student profile (student + attendance + assignments) |
| `POST` | `/api/update_student` | Admin | Edit a student's profile |
| `POST` | `/api/delete_record` | Admin | Delete an attendance or assignment record |

---

### ⚙️ C++ Backend Modules (DSA) — Phase 3 Complete

#### `login.cpp` — HashMap (`unordered_map`) | *Maitri Goyal*
- **Data Structure:** `unordered_map<string, Student>` for O(1) average-case student lookup.
- **Phase 3 Status:** Core lookup fully operational. Password validation handled in `app.py`; the C++ module performs the fast ID-to-profile resolution.
- **Input:** Target roll number on line 1, then CSV rows of all students.
- **Output:** Student profile as a JSON object.

#### `attendance.cpp` — Merge Sort | *Mohit Chandra Purohit*
- **Data Structure:** `vector<Subject>` sorted using recursive Merge Sort.
- **Phase 3 Addition — Attendance Predictor:**
  - `predictClasses(attended, total)` — calculates the **minimum consecutive classes** a student must attend to reach the 75% threshold.
  - `can_miss` — calculates how many more classes a student can safely skip while staying above 75%.
  - Formula: `x ≥ (0.75 × total − attended) / 0.25`
- **Output:** JSON array sorted ascending by percentage, each entry with `subject`, `percentage`, `warning` (bool), `classes_needed`, and `can_miss`.

#### `notices.cpp` — Trie + DFS Auto-Complete | *Shyamali Bisht*
- **Data Structure:** `Trie` with `TrieNode` children array (26 characters, case-insensitive).
- **`insert(category, notice)`** — indexes each notice by its category string character-by-character.
- **`search(category)`** — O(k) exact-match retrieval (k = category length).
- **Phase 3 Addition — `autoCompleteCategory(prefix)`:**
  - Navigates the Trie to the end of the prefix.
  - Performs a **DFS traversal** (`dfsCollect`) to enumerate all valid category completions.
  - Example: `autoCompleteCategory("e")` → `["event", "exam"]`
- **Output:** Filtered JSON array of notices.

#### `assignments.cpp` — Min-Heap | *Manisha Bisht*
- **Data Structure:** `MinHeap` backed by a `vector<Assignment>`, ordered by `dueDate` (lexicographic ISO-8601 date string comparison).
- **`insert(a)`** — Appends to vector and **bubble-up** loop restores heap property.
- **`extractMin()`** — Returns earliest-deadline assignment, replaces root with last element, calls `heapify()` to sift down.
- **Phase 3 Addition — `editDueDate(index, newDate)`:**
  - Updates a specific assignment's due date.
  - Restores heap property: **bubble-up** if new date is earlier, **sift-down** (`heapify`) if later.
- **Output:** JSON array of assignments in deadline-ascending order.

---

### 🖥️ Frontend — 9 HTML Pages

All pages share the `global.css` dark glassmorphism design system.

| Page | Features |
|---|---|
| `index.html` | Student login with Roll No + Password, link to Admission Form |
| `student_dashboard.html` | Stat cards (CGPA, Branch, Hostel, Room), navigation to all modules |
| `attendance.html` | Subject progress bars, color-coded warnings (<75%), live attendance predictor showing classes needed or classes that can be missed |
| `assignments.html` | Deadline cards sorted by nearest due date, countdown timers, first card highlighted as most urgent |
| `notices.html` | Category pill filter (All / Fee / Event / Exam / Academic), urgent notices highlighted |
| `clubs.html` | Club directory cards with enrollment %, open/limited/full status badges, coordinator info |
| `admission_form.html` | Public multi-step admission form; submits to `pending_admissions` table |
| `admin_login.html` | Admin authentication page |
| `admin.html` | Full admin dashboard (session-protected) — see Admin Panel section below |

---

### 🛡️ Admin Panel (`admin.html`)

Access at `/admin.html` after logging in at `/admin_login.html`.

**Default credentials:** `admin` / `admin123`

The admin panel has 6 tabs:

| Tab | Functionality |
|---|---|
| **Pending Admissions** | View all applications, upload multiple CSV files, select all, bulk-approve with auto-generated credentials |
| **Add Student** | Manually add a single student to the database |
| **Add Attendance** | Record subject-wise attendance for any student |
| **Add Assignment** | Create a new assignment for any student |
| **Add Notice** | Publish university announcements |
| **Manage Student** | Search by ID, edit profile, delete attendance/assignment records |

#### Bulk Enrollment Demo Flow
1. Run `python generate_dummy_csv.py` to create `dummy_students/` with 100 student CSV files.
2. In the Pending Admissions tab, click **📤 Upload CSVs**.
3. Navigate to `dummy_students/`, press `Ctrl+A` to select all 100 files, click **Open**.
4. The server parses all files and creates 100 pending applications.
5. Check **Select All** and click **✅ Approve Selected**.
6. The ERP instantly generates for each student:
   - **Roll Number** (e.g., `20260007`)
   - **College Email** (e.g., `20260007@gehu.ac.in`)
   - **Default Password** (= Roll Number)
   - **Section** (A / B / C based on branch headcount)
   - **Hostel + Room** (based on gender and hostel preference)

---

## 🚀 How to Run

### Prerequisites

```bash
# Python 3.8+
pip install flask flask-cors

# C++ compiler (for DSA modules)
# Windows: install MinGW and ensure g++ is in PATH
# Linux/Mac: sudo apt install g++ / brew install gcc
```

### Start the Server

```bash
cd GehuConnect--DAA-
python app.py
```

Then open: **http://localhost:5000**

The database (`gehuconnect.db`) is automatically created and seeded with sample data on the first run.

### Generate Dummy Student Data (for bulk enrollment demo)

```bash
python generate_dummy_csv.py
```

This creates `dummy_students/` containing 100 individual `.csv` files.

---

## 🔑 Demo Login Credentials

### Student Accounts

| Name | Roll No | Password |
|---|---|---|
| Mohit Purohit | `2419260` | `2419260` |
| Maitri Goyal | `2418628` | `2418628` |
| Manisha Bisht | `2419475` | `2419475` |
| Shyamali Bisht | `2418996` | `2418996` |

> **Default password for all students = their Roll Number.**
> Students approved via bulk enrollment also get their Roll Number as their default password.

### Admin Account

| Username | Password |
|---|---|
| `admin` | `admin123` |

---

## 🛠️ Tech Stack

| Layer | Technology | Details |
|---|---|---|
| Frontend | HTML5 + Vanilla CSS + Vanilla JS | Dark glassmorphism UI, micro-animations, responsive layout |
| Design System | `global.css` | CSS custom properties, shared tokens, utility classes |
| Backend API | Python 3 — Flask, Flask-CORS | REST API + server-side session auth |
| Database | SQLite (`sqlite3`) | 7 tables, auto-created, seeded with demo data |
| DSA Logic | C++17 (STL) | 4 modules compiled on-demand via `g++` at runtime |
| C++ Pipeline | Python `subprocess` | Flask calls `g++` to compile → runs binary with temp file → captures JSON stdout |

---

## 📌 Phase Roadmap

| Phase | Status | Description |
|---|---|---|
| **Phase 1** | ✅ Done | Project structure, login UI, basic Flask routing |
| **Phase 2** | ✅ Done | Flask + SQLite backend, 4 C++ DSA modules, 5 live HTML pages |
| **Phase 3** | ✅ Done | DSA stubs completed, session auth, admin panel, clubs, admission flow, bulk CSV enrollment, dark UI overhaul |

### Phase 3 Specific Completions

| Feature | Status | Description |
|---|---|---|
| Merge Sort (attendance.cpp) | ✅ Done | Full recursive merge sort with `merge()` function |
| Attendance Predictor | ✅ Done | `predictClasses()` + `can_miss` calculation |
| Trie Search (notices.cpp) | ✅ Done | O(k) exact-match category search |
| Trie Auto-Complete | ✅ Done | DFS `dfsCollect()` → `autoCompleteCategory(prefix)` |
| Min-Heap Insert (assignments.cpp) | ✅ Done | Bubble-up loop fully implemented |
| Min-Heap `editDueDate` | ✅ Done | Bubble-up or sift-down based on date comparison |
| Admin Dashboard | ✅ Done | Session-protected, 6-tab interface |
| Pending Admissions | ✅ Done | Review, select, and bulk approve applications |
| Auto-Credential Generation | ✅ Done | Roll No, Email, Section, Hostel, Room auto-assigned |
| Bulk CSV Upload | ✅ Done | Multi-file upload → parse → insert into pending_admissions |
| Clubs Module | ✅ Done | `/clubs` API + `clubs.html` with status badges |
| Admission Form | ✅ Done | Public-facing form → `pending_admissions` table |
| Global Dark UI | ✅ Done | Glassmorphism design system in `global.css` |
| Static Routing Fix | ✅ Done | HTML served from `Frontend/HTML/`, assets from `Frontend/` |

---

## 📄 License

This project is developed for academic purposes under the **Design & Analysis of Algorithms (DAA)** course at **Graphic Era Hill University, Dehradun**.
