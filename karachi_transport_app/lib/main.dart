import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const KarachiTransportApp());
}

class KarachiTransportApp extends StatelessWidget {
  const KarachiTransportApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Karachi Smart Transport Planner',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal, brightness: Brightness.light),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
