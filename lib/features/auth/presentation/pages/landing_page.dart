import 'package:flutter/cupertino.dart';
import 'package:flutter/material.dart';
import 'package:spill_sentinel/core/theme/app_pallete.dart';
import 'package:spill_sentinel/features/auth/presentation/pages/login_page.dart';
import 'package:spill_sentinel/features/auth/presentation/pages/signup_page.dart';
import 'package:spill_sentinel/features/auth/presentation/widgets/auth_button.dart';

class LandingPage extends StatefulWidget {
  const LandingPage({super.key});

  @override
  State<LandingPage> createState() => _LandingPageState();
}

class _LandingPageState extends State<LandingPage> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(0),
        child: Column(
          children: [
            // Header with Background Image
            SizedBox(
              width: MediaQuery.of(context).size.width,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Image(
                          image: AssetImage('assets/images/authBgImage.png'),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 30),
            // Main Content
            SizedBox(
              height: MediaQuery.of(context).size.height * 0.7,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    children: [
                      const Text(
                        "Welcome!",
                        style: TextStyle(
                          fontSize: 50,
                          fontWeight: FontWeight.w800,
                          color: Pallete.primaryColor,
                        ),
                      ),
                      const SizedBox(
                          height: 8), // Add spacing between text elements
                      Text(
                        "The best place to manage oil spills",
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w500,
                          color: Pallete
                              .whiteColor, // Use white for better contrast
                        ),
                      ),
                    ],
                  ),
                  SizedBox(
                    width: MediaQuery.of(context).size.width * 0.8,
                    child: const Hero(
                      tag: 'illustration',
                      child: Image(
                        image: AssetImage("assets/images/Illustration.png"),
                        fit: BoxFit.fitWidth,
                      ),
                    ),
                  ),
                  // Auth Buttons
                  Column(
                    children: [
                      AuthButton(
                        text: 'Sign Up',
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) => const SignUpPage(),
                            ),
                          );
                        },
                      ),
                      const SizedBox(height: 20),
                      AuthButton(
                        text: 'Log In',
                        onPressed: () {
                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (context) => const LoginPage(),
                            ),
                          );
                        },
                        isInverted: true,
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
