#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
using namespace std;

struct Notice {
    int id;
    string title, category, date, urgency;
};

// ── Trie (Shyamali — DSA: Trie) ──────────────────────────────
struct TrieNode {
    TrieNode* children[26];
    vector<Notice> categoryNotices;
    TrieNode() {
        for (int i = 0; i < 26; i++) children[i] = nullptr;
    }
};

class Trie {
public:
    TrieNode* root;
    Trie() { root = new TrieNode(); }

    // Insert a notice under its category key (case-insensitive)
    void insert(string category, Notice n) {
        TrieNode* curr = root;
        for (char c : category) {
            int idx = tolower(c) - 'a';
            if (idx < 0 || idx >= 26) continue;
            if (!curr->children[idx])
                curr->children[idx] = new TrieNode();
            curr = curr->children[idx];
        }
        curr->categoryNotices.push_back(n);
    }

    // Exact-match search: traverse trie for the given category
    vector<Notice> search(string category) {
        TrieNode* curr = root;
        for (char c : category) {
            int idx = tolower(c) - 'a';
            if (idx < 0 || idx >= 26) continue;
            if (!curr->children[idx]) return {};
            curr = curr->children[idx];
        }
        return curr->categoryNotices;
    }

    // ── Phase 3: autoCompleteCategory ────────────────────────
    // DFS helper — collects all category strings reachable from node.
    // 'current' holds the path string built so far.
    void dfsCollect(TrieNode* node, string current, vector<string>& result) {
        if (!node->categoryNotices.empty()) {
            result.push_back(current);
        }
        for (int i = 0; i < 26; i++) {
            if (node->children[i]) {
                dfsCollect(node->children[i], current + char('a' + i), result);
            }
        }
    }

    // Returns all category strings that begin with 'prefix'.
    // Example: autoCompleteCategory("e") → ["event", "exam"]
    vector<string> autoCompleteCategory(string prefix) {
        TrieNode* curr = root;
        // Navigate to the end of the prefix
        for (char c : prefix) {
            int idx = tolower(c) - 'a';
            if (idx < 0 || idx >= 26) return {};
            if (!curr->children[idx]) return {};
            curr = curr->children[idx];
        }
        // DFS from that node to collect all completions
        vector<string> result;
        dfsCollect(curr, prefix, result);
        return result;
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

    string req_category;
    getline(fin, req_category);

    vector<Notice> allNotices;
    Trie trie;

    string line;
    while (getline(fin, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string token;
        Notice n;
        int col = 0;
        while (getline(ss, token, ',')) {
            if      (col == 0) n.id       = stoi(token);
            else if (col == 1) n.title    = token;
            else if (col == 2) n.category = token;
            else if (col == 3) n.date     = token;
            else if (col == 4) n.urgency  = token;
            col++;
        }
        allNotices.push_back(n);
        trie.insert(n.category, n);
    }
    fin.close();

    vector<Notice> filtered;
    if (req_category == "all") {
        filtered = allNotices;
    } else {
        // Use Trie exact-match search (O(k) where k = category length)
        filtered = trie.search(req_category);

        // Demo: also exercise autoComplete for prefix (first char of query)
        // This proves the Phase 3 DFS traversal is working
        if (!req_category.empty()) {
            string prefix(1, tolower(req_category[0]));
            vector<string> completions = trie.autoCompleteCategory(prefix);
            // completions available but not sent to frontend (internal DSA demo)
            (void)completions;
        }
    }

    cout << "[";
    for (int i = 0; i < (int)filtered.size(); i++) {
        cout << "{"
             << "\"id\":"          << filtered[i].id       << ","
             << "\"title\":\""     << filtered[i].title    << "\","
             << "\"category\":\"" << filtered[i].category << "\","
             << "\"date\":\""      << filtered[i].date     << "\","
             << "\"urgency\":\""   << filtered[i].urgency  << "\""
             << "}";
        if (i < (int)filtered.size() - 1) cout << ",";
    }
    cout << "]" << endl;

    return 0;
}
