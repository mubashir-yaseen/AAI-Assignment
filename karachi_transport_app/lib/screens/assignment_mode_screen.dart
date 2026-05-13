import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../widgets/route_summary_card.dart';


const String baseUrl = "https://aai-assignment-backend.onrender.com"; // Replace with your actual Render URL
//const String baseUrl = "http://localhost:8000"; // Previous code when i was running on localhost

class AssignmentModeScreen extends StatefulWidget {
  const AssignmentModeScreen({super.key});
  @override
  State<AssignmentModeScreen> createState() => _AssignmentModeScreenState();
}

class _AssignmentModeScreenState extends State<AssignmentModeScreen> {
  List<String> nodes = [];
  String? startNode;
  String? goalNode;
  String selectedAlgo = "A*";
  String? selectedHeuristic = "h1";
  
  bool isLoadingNodes = true;
  bool isSearching = false;
  Map<String, dynamic>? resultData;
  String? errorMessage;

  final List<String> algorithms = ["BFS", "DFS", "UCS", "Greedy", "A*", "IDA*"];

  // Optimizer states
  int kStops = 10;
  bool isOptimizing = false;
  Map<String, dynamic>? optimizerResult;

  @override
  void initState() {
    super.initState();
    _fetchNodes();
  }

  Future<void> _fetchNodes() async {
    try {
      final res = await http.get(Uri.parse('$baseUrl/assignment/nodes'));
      if (res.statusCode == 200) {
        final List<dynamic> data = jsonDecode(res.body);
        setState(() {
          nodes = data.cast<String>();
          startNode = nodes.isNotEmpty ? nodes[0] : null;
          goalNode = nodes.length > 1 ? nodes[1] : (nodes.isNotEmpty ? nodes[0] : null);
          isLoadingNodes = false;
        });
      }
    } catch (e) {
      setState(() {
        isLoadingNodes = false;
        errorMessage = "Failed to connect to backend. Please ensure the FastAPI server is running on port 8000.";
      });
    }
  }

  Future<void> _runSearch() async {
    if (startNode == null || goalNode == null) return;
    setState(() { isSearching = true; resultData = null; errorMessage = null; });

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/assignment/route'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"start": startNode, "goal": goalNode, "algorithm": selectedAlgo, "heuristic": selectedHeuristic}),
      );

      if (res.statusCode == 200) setState(() => resultData = jsonDecode(res.body));
      else setState(() => errorMessage = jsonDecode(res.body)['detail'] ?? "Search failed.");
    } catch (e) {
      setState(() => errorMessage = "Network error: $e");
    } finally {
      setState(() => isSearching = false);
    }
  }

  Future<void> _runOptimizer() async {
    setState(() { isOptimizing = true; optimizerResult = null; errorMessage = null; });

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/assignment/local_search_optimize'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({"k_stops": kStops}),
      );

      if (res.statusCode == 200) setState(() => optimizerResult = jsonDecode(res.body));
      else setState(() => errorMessage = jsonDecode(res.body)['detail'] ?? "Optimization failed.");
    } catch (e) {
      setState(() => errorMessage = "Network error: $e");
    } finally {
      setState(() => isOptimizing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (isLoadingNodes) return const Center(child: CircularProgressIndicator());

    return DefaultTabController(
      length: 2,
      child: Column(
        children: [
          const TabBar(
            labelColor: Colors.teal,
            unselectedLabelColor: Colors.grey,
            tabs: [
              Tab(text: "Path Finding"),
              Tab(text: "Network Optimizer (L3)"),
            ],
          ),
          Expanded(
            child: TabBarView(
              children: [
                _buildPathFindingTab(),
                _buildNetworkOptimizerTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPathFindingTab() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(labelText: 'Start Location', border: OutlineInputBorder()),
                    value: startNode,
                    items: nodes.map((n) => DropdownMenuItem(value: n, child: Text(n))).toList(),
                    onChanged: (v) => setState(() => startNode = v),
                  ),
                  const SizedBox(height: 16),
                  DropdownButtonFormField<String>(
                    decoration: const InputDecoration(labelText: 'Goal Location', border: OutlineInputBorder()),
                    value: goalNode,
                    items: nodes.map((n) => DropdownMenuItem(value: n, child: Text(n))).toList(),
                    onChanged: (v) => setState(() => goalNode = v),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          decoration: const InputDecoration(labelText: 'Algorithm', border: OutlineInputBorder()),
                          value: selectedAlgo,
                          items: algorithms.map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
                          onChanged: (v) {
                            setState(() {
                              selectedAlgo = v!;
                              if (["BFS", "DFS", "UCS"].contains(v)) selectedHeuristic = null;
                              else selectedHeuristic ??= "h1";
                            });
                          },
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: DropdownButtonFormField<String?>(
                          decoration: const InputDecoration(labelText: 'Heuristic', border: OutlineInputBorder()),
                          value: selectedHeuristic,
                          items: const [
                            DropdownMenuItem(value: null, child: Text('None')),
                            DropdownMenuItem(value: "h1", child: Text('h1 (Distance)')),
                            DropdownMenuItem(value: "h2", child: Text('h2 (Informed)')),
                          ],
                          onChanged: ["BFS", "DFS", "UCS"].contains(selectedAlgo) ? null : (v) => setState(() => selectedHeuristic = v),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(minimumSize: const Size.fromHeight(50), backgroundColor: Theme.of(context).colorScheme.primary, foregroundColor: Theme.of(context).colorScheme.onPrimary),
                    icon: const Icon(Icons.search),
                    label: const Text('Run Search', style: TextStyle(fontSize: 16)),
                    onPressed: isSearching ? null : _runSearch,
                  ),
                ],
              ),
            ),
          ),
          if (errorMessage != null) Padding(padding: const EdgeInsets.only(top: 16), child: Text(errorMessage!, style: const TextStyle(color: Colors.red))),
          const SizedBox(height: 16),
          if (isSearching) const Center(child: CircularProgressIndicator())
          else if (resultData != null) Expanded(child: ListView(children: [RouteSummaryCard(data: resultData!)])),
        ],
      ),
    );
  }

  Widget _buildNetworkOptimizerTab() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Card(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  const Text("Optimize the transport network by selecting K active bus stops.", style: TextStyle(fontSize: 14)),
                  const SizedBox(height: 16),
                  TextFormField(
                    initialValue: kStops.toString(),
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(
                      labelText: 'Number of Active Stops (K)',
                      border: OutlineInputBorder(),
                    ),
                    onChanged: (v) {
                      final parsed = int.tryParse(v);
                      if (parsed != null) setState(() => kStops = parsed);
                    },
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size.fromHeight(50), 
                      backgroundColor: Colors.teal, 
                      foregroundColor: Colors.white
                    ),
                    icon: const Icon(Icons.network_check),
                    label: const Text('Optimize Bus Network', style: TextStyle(fontSize: 16)),
                    onPressed: isOptimizing ? null : _runOptimizer,
                  ),
                ],
              ),
            ),
          ),
          if (errorMessage != null) Padding(padding: const EdgeInsets.only(top: 16), child: Text(errorMessage!, style: const TextStyle(color: Colors.red))),
          const SizedBox(height: 16),
          if (isOptimizing) 
            const Center(child: Column(
              children: [
                CircularProgressIndicator(),
                SizedBox(height: 10),
                Text("Running Simulated Annealing..."),
              ],
            ))
          else if (optimizerResult != null) 
            Expanded(child: ListView(children: [RouteSummaryCard(data: optimizerResult!)])),
        ],
      ),
    );
  }
}
