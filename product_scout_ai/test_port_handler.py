#!/usr/bin/env python3
"""
测试端口处理功能
"""
import sys
import os

# Add current directory to path to import our functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_app import check_port_available, kill_process_on_port

def test_port_handler():
    """测试端口处理功能"""
    print("🧪 测试端口处理功能...")
    print("=" * 50)

    test_port = 7860

    # 1. 检查当前端口状态
    print(f"1️⃣ 检查端口 {test_port} 状态...")
    if check_port_available(test_port):
        print(f"✅ 端口 {test_port} 可用")
    else:
        print(f"❌ 端口 {test_port} 被占用")

    # 2. 测试端口处理函数
    print(f"\n2️⃣ 测试端口处理函数...")
    result = kill_process_on_port(test_port)
    if result:
        print(f"✅ 端口处理成功")
    else:
        print(f"❌ 端口处理失败")

    # 3. 再次检查端口状态
    print(f"\n3️⃣ 再次检查端口状态...")
    if check_port_available(test_port):
        print(f"✅ 端口 {test_port} 现在可用")
        return True
    else:
        print(f"❌ 端口 {test_port} 仍被占用")
        return False

if __name__ == "__main__":
    success = test_port_handler()
    print(f"\n📊 测试结果: {'✅ 成功' if success else '❌ 失败'}")
    sys.exit(0 if success else 1)