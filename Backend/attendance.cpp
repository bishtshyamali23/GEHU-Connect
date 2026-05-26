#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <cmath>
using namespace std;

// Each subject stores name + percentage (out of 100)
struct Subject {
    string name;
    float percentage;
};

// ── Merge Sort (Mohit — DSA: Merge Sort) ─────────────────────
void merge(vector<Subject>& arr, int left, int mid, int right) {
    int n1 = mid - left + 1;
    int n2 = right - mid;
    vector<Subject> L(n1), R(n2);
    for (int i = 0; i < n1; i++) L[i] = arr[left + i];
    for (int j = 0; j < n2; j++) R[j] = arr[mid + 1 + j];
    int i = 0, j = 0, k = left;
    while (i < n1 && j < n2) {
        if (L[i].percentage <= R[j].percentage)
            arr[k++] = L[i++];
        else
            arr[k++] = R[j++];
    }
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];
}

void mergeSort(vector<Subject>& arr, int left, int right) {
    if (left >= right) return;
    int mid = left + (right - left) / 2;
    mergeSort(arr, left, mid);
    mergeSort(arr, mid + 1, right);
    merge(arr, left, mid, right);
}

// ── Phase 3: Attendance Predictor ────────────────────────────
// Calculates how many consecutive classes a student must attend
// to reach the 75% threshold, assuming TOTAL_CLASSES per semester.
// Formula derivation:
//   (attended + x) / (total + x) >= 0.75
//   attended + x  >= 0.75*total + 0.75*x
//   0.25*x        >= 0.75*total - attended
//   x             >= (0.75*total - attended) / 0.25
const float TOTAL_CLASSES = 40.0f;

int predictClasses(float attended, float total) {
    float needed = 0.75f * total - attended;
    if (needed <= 0) return 0;
    return (int)ceil(needed / 0.25f);
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "{\"error\":\"Missing temp file argument\"}" << endl;
        return 1;
    }
    ifstream fin(argv[1]);
    if (!fin.is_open()) {
        cout << "{\"error\":\"temp file missing\"}" << endl;
        return 1;
    }

    vector<Subject> subjects;
    string line;
    while (getline(fin, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string name, pct;
        getline(ss, name, ',');
        getline(ss, pct, ',');
        subjects.push_back({name, stof(pct)});
    }
    fin.close();

    // Sort ascending by attendance % using Merge Sort
    if (!subjects.empty()) {
        mergeSort(subjects, 0, (int)subjects.size() - 1);
    }

    cout << "[";
    for (int i = 0; i < (int)subjects.size(); i++) {
        float pct       = subjects[i].percentage;
        float attended  = pct * TOTAL_CLASSES / 100.0f;
        bool  warning   = (pct < 75.0f);

        // Attendance predictor (Phase 3)
        int classes_needed = 0;
        int can_miss       = 0;
        if (warning) {
            classes_needed = predictClasses(attended, TOTAL_CLASSES);
        } else {
            // How many more classes can they afford to skip?
            // (attended - x) / TOTAL >= 0.75  =>  x <= attended - 0.75*TOTAL
            int cm = (int)floor(attended - 0.75f * TOTAL_CLASSES);
            can_miss = (cm > 0) ? cm : 0;
        }

        cout << "{"
             << "\"subject\":\""    << subjects[i].name << "\","
             << "\"percentage\":"   << pct              << ","
             << "\"warning\":"      << (warning ? "true" : "false") << ","
             << "\"classes_needed\":" << classes_needed << ","
             << "\"can_miss\":"     << can_miss
             << "}";
        if (i < (int)subjects.size() - 1) cout << ",";
    }
    cout << "]" << endl;

    return 0;
}
