#!/usr/bin/env python3
"""
Simple test script to debug Gradio app startup.
"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

print("🔍 Testing imports...")

try:
    print("1. Importing gradio...")
    import gradio as gr
    print("✅ gradio imported")
except Exception as e:
    print(f"❌ gradio import failed: {e}")
    sys.exit(1)

try:
    print("2. Testing simple Gradio app...")

    def hello(name):
        return f"Hello {name}!"

    # Create minimal app
    app = gr.Interface(fn=hello, inputs="text", outputs="text")
    print("✅ Simple app created")

    print("3. Launching test app...")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True
    )

except Exception as e:
    print(f"❌ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)