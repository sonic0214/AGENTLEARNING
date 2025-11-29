#!/usr/bin/env python3
"""
专门诊断UI导入问题
"""
import sys
import os

# Add src to Python path
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
sys.path.insert(0, src_path)

def test_ui_imports_step_by_step():
    """逐步测试UI组件导入"""
    print("🔍 逐步诊断UI导入问题...")
    print("=" * 50)

    # 测试基础模块
    print("1. 测试基础UI模块导入...")
    try:
        import gradio as gr
        print("   ✅ gradio 导入成功")
    except Exception as e:
        print(f"   ❌ gradio 导入失败: {e}")
        return False

    # 测试utils.theme
    print("\n2. 测试 utils.theme 导入...")
    try:
        from src.ui.utils.theme import get_custom_css, THEME_COLORS
        print("   ✅ utils.theme 导入成功")
    except Exception as e:
        print(f"   ❌ utils.theme 导入失败: {e}")
        return False

    # 测试components.charts
    print("\n3. 测试 components.charts 导入...")
    try:
        from src.ui.components.charts import create_radar_chart, create_bar_chart
        print("   ✅ components.charts 导入成功")
    except Exception as e:
        print(f"   ❌ components.charts 导入失败: {e}")
        return False

    # 测试其他components
    print("\n4. 测试其他components导入...")
    try:
        from src.ui.components.score_cards import create_score_cards
        print("   ❌ create_score_cards 不存在!")

        from src.ui.components.score_cards import format_score_card, format_overall_score
        from src.ui.components.result_panels import create_result_panels
        print("   ✅ 正确的components导入成功")
    except Exception as e:
        print(f"   ❌ 其他components导入失败: {e}")
        return False

    # 测试tabs
    print("\n5. 测试tabs导入...")
    try:
        from src.ui.tabs.analysis_tab import create_analysis_tab
        from src.ui.tabs.history_tab import create_history_tab
        from src.ui.tabs.comparison_tab import create_comparison_tab
        from src.ui.tabs.export_tab import create_export_tab
        print("   ✅ tabs导入成功")
    except Exception as e:
        print(f"   ❌ tabs导入失败: {e}")
        return False

    # 测试handlers
    print("\n6. 测试handlers导入...")
    try:
        from src.ui.handlers.analysis_handlers import run_analysis
        from src.ui.handlers.history_handlers import get_history, clear_history
        from src.ui.handlers.export_handlers import export_to_csv, export_to_json
        print("   ✅ handlers导入成功")
    except Exception as e:
        print(f"   ❌ handlers导入失败: {e}")
        return False

    # 测试完整app
    print("\n7. 测试完整app导入...")
    try:
        from src.ui.app import create_app, main
        print("   ✅ 完整app导入成功")
    except Exception as e:
        print(f"   ❌ 完整app导入失败: {e}")
        return False

    return True

def test_app_creation():
    """测试app创建"""
    print("\n🔧 测试应用创建...")

    try:
        from src.ui.app import create_app
        app = create_app()
        print("   ✅ 应用创建成功")
        print(f"   ✅ 应用类型: {type(app)}")
        return True
    except Exception as e:
        print(f"   ❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🎯 UI导入诊断工具")
    print("=" * 80)

    # 逐步测试导入
    if test_ui_imports_step_by_step():
        print("\n✅ 所有UI导入测试通过")

        # 测试应用创建
        if test_app_creation():
            print("\n🎉 UI模块完全正常!")
            return 0
        else:
            print("\n❌ 应用创建失败")
            return 1
    else:
        print("\n❌ UI导入测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())