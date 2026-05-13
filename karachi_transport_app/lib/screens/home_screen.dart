import 'package:flutter/material.dart';
import 'assignment_mode_screen.dart';
import 'real_mode_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Karachi Smart Transport Planner', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
        centerTitle: true,
        backgroundColor: Theme.of(context).colorScheme.primaryContainer,
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: SegmentedButton<int>(
              segments: const [
                ButtonSegment(value: 0, label: Text('Assignment Mode'), icon: Icon(Icons.school)),
                ButtonSegment(value: 1, label: Text('Real Karachi Mode'), icon: Icon(Icons.map)),
              ],
              selected: {_selectedIndex},
              onSelectionChanged: (newSelection) => setState(() => _selectedIndex = newSelection.first),
            ),
          ),
          Expanded(
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 300),
              child: _selectedIndex == 0 ? const AssignmentModeScreen() : const RealModeScreen(),
            ),
          ),
        ],
      ),
    );
  }
}
