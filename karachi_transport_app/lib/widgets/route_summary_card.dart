import 'package:flutter/material.dart';

class RouteSummaryCard extends StatelessWidget {
  final Map<String, dynamic> data;
  const RouteSummaryCard({super.key, required this.data});

  @override
  Widget build(BuildContext context) {
    final bool isReal = data['mode'] == 'real';
    final bool isOptimizer = data['mode'] == 'optimizer';
    
    return Card(
      elevation: 4,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(isOptimizer ? Icons.network_check : Icons.route, color: Colors.teal),
                const SizedBox(width: 8),
                Text(isOptimizer ? 'Optimization Results' : 'Route Summary', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              ],
            ),
            const Divider(),
            if (isOptimizer) ...[
              _buildRow(Icons.score, 'Objective Value', '${data['objective']}'),
              _buildRow(Icons.location_on, 'Selected Stops', (data['best_stops'] as List).join(', ')),
              _buildRow(Icons.link, 'Connections (First 5)', _formatConnections(data['best_connections'])),
            ] else if (!isReal) ...[
              _buildRow(Icons.directions, 'Path', data['path'].join(' → ')),
              _buildRow(Icons.timer, 'Time Cost', '${data['cost_minutes']} mins'),
            ] else ...[
              _buildRow(Icons.straighten, 'Distance', '${data['distance_km']} km'),
              _buildRow(Icons.timer, 'Graph Time', '${data['graph_time_minutes']} mins'),
              _buildRow(Icons.speed, 'Constant Speed Time', '${data['constant_speed_minutes']} mins'),
            ],
            if (!isOptimizer) ...[
              _buildRow(Icons.account_tree, 'Nodes Expanded', '${data['nodes_expanded']}'),
              _buildRow(Icons.layers, 'Max Frontier', '${data['max_frontier']}'),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: [
                  Chip(label: Text('Algo: ${data['algorithm']}'), backgroundColor: Colors.teal.shade100),
                  if (data['heuristic'] != null)
                    Chip(label: Text('Heuristic: ${data['heuristic']}'), backgroundColor: Colors.orange.shade100),
                ],
              ),
            ]
          ],
        ),
      ),
    );
  }

  String _formatConnections(List<dynamic> conns) {
    if (conns.isEmpty) return "None";
    final take = conns.take(5).map((e) => "${e[0]} ↔ ${e[1]}").join('\n');
    if (conns.length > 5) return "$take\n... and ${conns.length - 5} more";
    return take;
  }

  Widget _buildRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: Colors.grey.shade700),
          const SizedBox(width: 8),
          Text('$label: ', style: const TextStyle(fontWeight: FontWeight.bold)),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
