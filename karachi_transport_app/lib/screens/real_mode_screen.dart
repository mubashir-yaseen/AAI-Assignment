import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../widgets/route_summary_card.dart';

const String baseUrl = "http://localhost:8000";

class RealModeScreen extends StatefulWidget {
  const RealModeScreen({super.key});
  @override
  State<RealModeScreen> createState() => _RealModeScreenState();
}

class _RealModeScreenState extends State<RealModeScreen> {
  LatLng? source;
  LatLng? destination;
  List<LatLng> routePoints = [];
  
  String selectedAlgo = "A*";
  String? selectedHeuristic = "h1";
  bool isSearching = false;
  Map<String, dynamic>? resultData;
  String? errorMessage;
  
  final MapController mapController = MapController();
  final LatLng karachiCenter = const LatLng(24.8607, 67.0011);
  final TextEditingController sourceController = TextEditingController();
  final TextEditingController destController = TextEditingController();

  Future<void> _searchLocation(String query, bool isSource) async {
    if (query.isEmpty) return;
    try {
      final url = Uri.parse('https://nominatim.openstreetmap.org/search?q=$query, Karachi&format=json&limit=1');
      final response = await http.get(url);
      if (response.statusCode == 200) {
        final List data = jsonDecode(response.body);
        if (data.isNotEmpty) {
          final lat = double.parse(data[0]['lat']);
          final lon = double.parse(data[0]['lon']);
          setState(() {
            final point = LatLng(lat, lon);
            if (isSource) {
              source = point;
              sourceController.text = data[0]['display_name'].split(',')[0];
            } else {
              destination = point;
              destController.text = data[0]['display_name'].split(',')[0];
            }
            mapController.move(point, 14.0);
          });
        }
      }
    } catch (e) {
      // Ignore network errors gracefully
    }
  }

  void _handleTap(TapPosition tapPosition, LatLng point) {
    setState(() {
      if (source == null) source = point;
      else if (destination == null) destination = point;
      else { source = point; destination = null; routePoints.clear(); resultData = null; }
    });
  }

  Future<void> _findRoute() async {
    if (source == null || destination == null) return;
    setState(() { isSearching = true; errorMessage = null; });

    try {
      final res = await http.post(
        Uri.parse('$baseUrl/real/route'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          "source_lat": source!.latitude, "source_lon": source!.longitude,
          "dest_lat": destination!.latitude, "dest_lon": destination!.longitude,
          "algorithm": selectedAlgo, "heuristic": selectedHeuristic, "speed_kmh": 25.0
        }),
      );

      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        setState(() {
          resultData = data;
          routePoints = (data['path_latlon'] as List).map((p) => LatLng(p[0], p[1])).toList();
          if (routePoints.isNotEmpty) {
            final bounds = LatLngBounds.fromPoints(routePoints);
            mapController.fitCamera(CameraFit.bounds(bounds: bounds, padding: const EdgeInsets.all(50)));
          }
        });
      } else setState(() => errorMessage = jsonDecode(res.body)['detail'] ?? "Search failed.");
    } catch (e) {
      setState(() => errorMessage = "Network error: $e");
    } finally {
      setState(() => isSearching = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(
          flex: 3,
          child: Stack(
            children: [
              FlutterMap(
                mapController: mapController,
                options: MapOptions(initialCenter: karachiCenter, initialZoom: 12.0, onTap: _handleTap),
                children: [
                  TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png', userAgentPackageName: 'com.example.app'),
                  PolylineLayer(polylines: [if (routePoints.isNotEmpty) Polyline(points: routePoints, color: Colors.deepPurple, strokeWidth: 7.0)]),
                  MarkerLayer(
                    markers: [
                      if (source != null) Marker(point: source!, child: const Icon(Icons.location_on, color: Colors.green, size: 40)),
                      if (destination != null) Marker(point: destination!, child: const Icon(Icons.location_on, color: Colors.red, size: 40)),
                    ],
                  ),
                ],
              ),
              Positioned(
                top: 8, left: 8, right: 8,
                child: Card(
                  child: Padding(
                    padding: const EdgeInsets.all(8.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Row(
                          children: [
                            Expanded(child: TextField(controller: sourceController, decoration: const InputDecoration(hintText: 'Search Source (e.g. Saddar)', isDense: true))),
                            IconButton(icon: const Icon(Icons.search, color: Colors.green), onPressed: () => _searchLocation(sourceController.text, true)),
                          ],
                        ),
                        Row(
                          children: [
                            Expanded(child: TextField(controller: destController, decoration: const InputDecoration(hintText: 'Search Destination (e.g. Clifton)', isDense: true))),
                            IconButton(icon: const Icon(Icons.search, color: Colors.red), onPressed: () => _searchLocation(destController.text, false)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        Text(
                          source == null ? "Search or tap map to set Source" : destination == null ? "Search or tap map to set Destination" : "Ready to find route",
                          textAlign: TextAlign.center, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ),
              )
            ],
          ),
        ),
        Expanded(
          flex: 2,
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: DropdownButtonFormField<String>(
                          decoration: const InputDecoration(labelText: 'Algorithm', border: OutlineInputBorder()),
                          value: selectedAlgo,
                          items: ["UCS", "Greedy", "A*", "IDA*"].map((a) => DropdownMenuItem(value: a, child: Text(a))).toList(),
                          onChanged: (v) {
                            setState(() {
                              selectedAlgo = v!;
                              if (v == "UCS") selectedHeuristic = null;
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
                            DropdownMenuItem(value: "h1", child: Text('h1')),
                            DropdownMenuItem(value: "h2", child: Text('h2')),
                          ],
                          onChanged: selectedAlgo == "UCS" ? null : (v) => setState(() => selectedHeuristic = v),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton.icon(
                    style: ElevatedButton.styleFrom(minimumSize: const Size.fromHeight(50), backgroundColor: Theme.of(context).colorScheme.primary, foregroundColor: Theme.of(context).colorScheme.onPrimary),
                    icon: isSearching ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2)) : const Icon(Icons.directions),
                    label: const Text('Find Route', style: TextStyle(fontSize: 16)),
                    onPressed: (isSearching || source == null || destination == null) ? null : _findRoute,
                  ),
                  if (errorMessage != null) Padding(padding: const EdgeInsets.only(top: 8), child: Text(errorMessage!, style: const TextStyle(color: Colors.red))),
                  if (resultData != null) Padding(padding: const EdgeInsets.only(top: 16), child: RouteSummaryCard(data: resultData!)),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
