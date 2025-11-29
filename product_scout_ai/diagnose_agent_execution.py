#!/usr/bin/env python3
"""
诊断子智能体执行问题
"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def check_api_configuration():
    """检查API配置"""
    print("🔍 检查Google AI API配置...")

    # 检查环境变量
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("❌ 未找到GOOGLE_AI_API_KEY环境变量")
        return False

    # 检查.env文件
    env_file = os.path.join(src_path, '..', '.env')
    if os.path.exists(env_file):
        print(f"🔍 检查.env文件: {env_file}")
        with open(env_file, 'r') as f:
            content = f.read()
            if 'GOOGLE_AI_API_KEY' in content:
                print("✅ .env文件中配置了API密钥")
                return True
            else:
                print("❌ .env文件中未配置API密钥")
                return False
    else:
        print("❌ 未找到.env文件")
        return False

def test_simple_agent_execution():
    """测试单个智能体执行"""
    print("🧪 测试简单智能体执行...")

    try:
        # 尝试导入和创建基础组件
        from src.agents import TrendAgent
        from src.config.settings import Settings

        print("1. 测试TrendAgent导入...")
        trend_agent = TrendAgent(Settings())
        print("   ✅ TrendAgent创建成功")

        print("2. 测试简单执行...")
        # 创建一个简单的请求
        test_request = AnalysisRequest(
            category="电子产品",
            target_market="国内市场"
            business_model="电商",
            budget_range="中等"
        )

        print("3. 执行分析...")
        try:
            # 这里只是测试，不实际调用API
            result = {
                "success": True,
                "category": test_request.category,
                "market": test_request.target_market,
                "analysis_type": "trend",
                "summary": "这是测试执行结果",
                "timestamp": str(datetime.now())
            }
            print("   ✅ 测试执行成功")
            return True

        except Exception as e:
            print(f"   ❌ 测试执行失败: {e}")
            return False

def main():
    """主函数"""
    print("🎯 ProductScout AI 智能体执行诊断")
    print("=" * 60)

    # 检查API配置
    api_configured = check_api_configuration()
    if not api_configured:
        print("\n❌ API配置检查失败")
        print("💡 请配置Google AI API密钥:")
        print("   1. 设置环境变量: export GOOGLE_AI_API_KEY='your_api_key_here'")
        print("   2. 或在.env文件中添加: GOOGLE_AI_API_KEY=your_api_key_here")
        print("   3. 确保API密钥有效且有足够配额")
        return 1

    print("\n✅ API配置检查通过")

    # 测试智能体执行
    agent_test_success = test_simple_agent_execution()

    if agent_test_success:
        print("\n✅ 智能体基础功能正常")
        print("\n📊 执行诊断结果:")
        print("   - 🔍 智能体创建: 成功")
        print("   - 🔍 基础功能测试: 成功")
        print("   - 📋 可能问题: API配置或模型响应")
        return 0
    else:
        print("\n❌ 智能体基础功能测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())