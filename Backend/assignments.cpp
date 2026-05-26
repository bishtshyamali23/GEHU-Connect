#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

struct Assignment {
    string subject, title, dueDate;
};

// ── Min-Heap (Manisha — DSA: Min-Heap) ───────────────────────
class MinHeap {
    vector<Assignment> heap;

    // Sift-down: restore heap property downward from index i
    void heapify(int i) {
        int smallest = i;
        int left  = 2 * i + 1;
        int right = 2 * i + 2;
        if (left  < (int)heap.size() && heap[left].dueDate  < heap[smallest].dueDate) smallest = left;
        if (right < (int)heap.size() && heap[right].dueDate < heap[smallest].dueDate) smallest = right;
        if (smallest != i) {
            swap(heap[i], heap[smallest]);
            heapify(smallest);
        }
    }

public:
    // Insert with bubble-up to maintain heap property
    void insert(Assignment a) {
        heap.push_back(a);
        int i = (int)heap.size() - 1;
        // Bubble up while parent has a later due-date
        while (i > 0 && heap[(i - 1) / 2].dueDate > heap[i].dueDate) {
            swap(heap[i], heap[(i - 1) / 2]);
            i = (i - 1) / 2;
        }
    }

    // Extract the assignment with the nearest due date (min)
    Assignment extractMin() {
        Assignment top = heap[0];
        heap[0] = heap.back();
        heap.pop_back();
        if (!heap.empty()) heapify(0);
        return top;
    }

    bool empty() { return heap.empty(); }
    int  size()  { return (int)heap.size(); }

    // ── Phase 3: editDueDate ──────────────────────────────────
    // Updates the due-date of the assignment at 'index' and
    // restores the Min-Heap property by either bubbling up
    // (if the new date is earlier) or sifting down (if later).
    void editDueDate(int index, string newDate) {
        if (index < 0 || index >= (int)heap.size()) return;
        string oldDate = heap[index].dueDate;
        heap[index].dueDate = newDate;

        if (newDate < oldDate) {
            // New date is earlier — bubble up toward root
            while (index > 0 && heap[(index - 1) / 2].dueDate > heap[index].dueDate) {
                swap(heap[index], heap[(index - 1) / 2]);
                index = (index - 1) / 2;
            }
        } else {
            // New date is later — sift down to restore property
            heapify(index);
        }
    }
};

int main(int argc, char* argv[]) {
    if (argc < 2) {
        cout << "{\"error\":\"Missing temp file argument\"}" << endl;
        return 1;
    }
    ifstream fin(argv[1]);
    if (!fin.is_open()) {
        cout << "{\"error\":\"input file missing\"}" << endl;
        return 1;
    }

    MinHeap pq;
    string line;
    while (getline(fin, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string sub, title, date;
        getline(ss, sub,   ',');
        getline(ss, title, ',');
        getline(ss, date,  ',');
        pq.insert({sub, title, date});
    }
    fin.close();

    cout << "[";
    bool first = true;
    while (!pq.empty()) {
        if (!first) cout << ",";
        Assignment a = pq.extractMin();
        cout << "{"
             << "\"subject\":\""  << a.subject << "\","
             << "\"title\":\""    << a.title   << "\","
             << "\"due_date\":\"" << a.dueDate << "\""
             << "}";
        first = false;
    }
    cout << "]" << endl;

    return 0;
}
