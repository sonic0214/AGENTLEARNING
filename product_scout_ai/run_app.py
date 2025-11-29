#!/usr/bin/env python3
"""
Direct runner for ProductScout AI Gradio application.

This script bypasses CLI issues and directly runs the Gradio app.
Enhanced with port conflict detection and resolution.
"""
import sys
import os
import subprocess
import socket
import time

def check_port_available(port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)
            result = s.connect_ex(('localhost', port))
            return result != 0
    except:
        return False

def kill_process_on_port(port):
    """终止占用指定端口的进程"""
    print(f"🔍 检查端口 {port} 是否被占用...")

    if check_port_available(port):
        print(f"✅ 端口 {port} 可用")
        return True

    print(f"⚠️  端口 {port} 被占用，尝试终止占用进程...")

    try:
        # 使用 lsof 查找占用端口的进程
        result = subprocess.run(
            ['lsof', '-t', f'-i:{port}'],
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    # 先尝试温和终止
                    subprocess.run(['kill', pid], check=False)
                    print(f"🔄 发送终止信号给进程 {pid}")

                    # 等待1秒
                    time.sleep(1)

                    # 检查进程是否还存在
                    kill_result = subprocess.run(['kill', '-0', pid], capture_output=True)
                    if kill_result.returncode == 0:
                        # 如果还存在，强制终止
                        subprocess.run(['kill', '-9', pid], check=False)
                        print(f"⚡ 强制终止进程 {pid}")

                except Exception as e:
                    print(f"⚠️  终止进程 {pid} 时出错: {e}")

            # 等待端口释放
            for i in range(5):
                time.sleep(1)
                if check_port_available(port):
                    print(f"✅ 端口 {port} 已释放")
                    return True
                print(f"⏳ 等待端口释放... ({i+1}/5)")

            return check_port_available(port)
        else:
            print(f"✅ 没有找到占用端口 {port} 的进程")
            return True

    except Exception as e:
        print(f"❌ 处理端口 {port} 冲突时出错: {e}")
        return False

def check_requirements():
    """Check if required packages are installed."""
    print("🔍 Checking requirements...")

    required_packages = {
        'gradio': 'gradio',
        'google-adk': 'google.adk',
        'google-generativeai': 'google.generativeai'
    }
    missing_packages = []

    for display_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"✅ {display_name}: installed")
        except ImportError:
            print(f"❌ {display_name}: NOT INSTALLED")
            missing_packages.append(display_name)

    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("💡 Install with: pip install {' '.join(missing_packages)}")
        return False
    else:
        print("✅ All requirements satisfied")
        return True

def run_gradio_app():
    """Run the Gradio application directly."""
    print("🚀 Starting Gradio application...")

    # Add src to Python path
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    sys.path.insert(0, src_path)

    # Run the app
    try:
        import ui.app
        from ui.app import main

        # Set default arguments
        server_name = "0.0.0.0"
        server_port = 7860
        share = False
        debug = True

        print("✅ Running Gradio app...")
        print(f"📍 Server: {server_name}:{server_port}")
        print(f"🔧 Debug: {debug}")
        print(f"🔗 Share: {share}")

        # Run the app
        main(
            server_name=server_name,
            server_port=server_port,
            share=share,
            debug=debug
        )

    except Exception as e:
        print(f"❌ Failed to run Gradio app: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def install_missing_packages():
    """Install missing packages."""
    print("📦 Installing missing packages...")

    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install",
            "gradio", "google-adk", "google-generativeai"
        ])
        print("✅ Packages installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install packages: {e}")
        return False

def main():
    """Main function."""
    print("🎯 ProductScout AI Launcher")
    print("=" * 80)

    # Step 1: Check requirements
    if not check_requirements():
        print("\n📦 Attempting to install missing packages...")
        if install_missing_packages():
            print("✅ Installation completed, retrying requirement check...")
            if not check_requirements():
                print("❌ Still missing packages after installation")
                return 1
            print("✅ All requirements satisfied!")
        else:
            print("❌ Failed to install missing packages")
            return 1
    else:
        print("✅ All requirements satisfied!")

    # Step 2: Handle port conflicts
    server_port = 7860
    if not kill_process_on_port(server_port):
        print(f"\n❌ 无法释放端口 {server_port}，请手动终止相关进程")
        print(f"💡 您可以运行以下命令手动检查和终止：")
        print(f"   lsof -i :{server_port}  # 查看占用进程")
        print(f"   kill -9 <PID>        # 终止进程")
        return 1

    # Step 3: Run app
    success = run_gradio_app()

    if success:
        print("\n🎉 Application started successfully!")
        print("🌐 Web interface should be available at: http://localhost:7860")
        print("\n💡 If the browser doesn't open automatically, try:")
        print("   http://localhost:7860")
        print("\n🔧 To stop the server, press Ctrl+C")
    else:
        print("\n❌ Failed to start application!")
        print("💡 如果看到 'address already in use' 错误，说明端口仍被占用")
        print("💡 请等待几秒后重新运行脚本")
        return 1

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())