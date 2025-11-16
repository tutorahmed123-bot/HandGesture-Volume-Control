#!/usr/bin/env python3
"""
Hand Gesture Volume Control - Main Entry Point
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main function to run the volume control"""
    print("🎵 Hand Gesture Volume Control")
    print("=" * 40)
    print("Controls:")
    print("• Open hand → Volume increases (visual)")
    print("• Closed hand → Volume decreases (visual)") 
    print("• Press Q to quit")
    print("=" * 40)
    
    try:
        from volume_control import DynamicHandVolumeControl
        controller = DynamicHandVolumeControl()
        controller.run()
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure you installed the requirements!")
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
