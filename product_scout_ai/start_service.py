#!/usr/bin/env python3
"""
ProductScout AI 启动脚本

解决了以下问题：
1. 包导入检查
2. Python路径设置
3. Gradio版本兼容性
4. 服务启动配置
"""
import sys
import os
import subprocess

def check_and_install_requirements():
    """检查并安装必要的依赖包"""
    print("🔍 检查依赖包...")

    requirements = {
        'gradio': 'gradio',
        'google-adk': 'google.adk',
        'google-generativeai': 'google.generativeai',
        'plotly': 'plotly',
        'pandas': 'pandas'
    }

    missing_packages = []

    for display_name, import_name in requirements.items():
        try:
            __import__(import_name)
            print(f"✅ {display_name}: 已安装")
        except ImportError:
            print(f"❌ {display_name}: 未安装")
            missing_packages.append(display_name)

    if missing_packages:
        print(f"📦 安装缺失的包: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ 包安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 包安装失败: {e}")
            return False
    else:
        print("✅ 所有依赖包都已安装")
        return True

def create_minimal_app():
    """创建最小化的Gradio应用"""
    print("🚀 创建最小化应用...")

    # Add src to Python path
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    sys.path.insert(0, src_path)

    import gradio as gr

    def analyze_product(product_name):
        """简单的产品分析函数"""
        if not product_name:
            return "请输入产品名称"

        # 模拟分析结果
        result = f"""
        ## 📊 产品分析结果

        **产品名称**: {product_name}

        ### 分析维度:
        - **市场趋势**: 🟡 需要深入分析
        - **竞争分析**: 🟡 需要深入分析
        - **盈利潜力**: 🟡 需要深入分析
        - **市场机会**: 🟡 需要深入分析

        ---
        *这是ProductScout AI的基础版本。完整功能需要配置API密钥。*
        """
        return result

    # 创建Gradio界面
    with gr.Blocks(title="ProductScout AI - 产品机会分析") as app:
        gr.Markdown("""
        # 🔍 ProductScout AI

        ### 智能产品机会分析平台

        基于 AI 多智能体技术，从趋势、市场、竞争和利润四个维度全面评估产品机会。
        """)

        gr.Markdown("---")
        gr.Markdown("## 📝 产品分析")

        with gr.Row():
            product_input = gr.Textbox(
                placeholder="请输入您想分析的产品名称...",
                label="产品名称",
                lines=1
            )

        with gr.Row():
            analyze_btn = gr.Button("🚀 开始分析", variant="primary")

        with gr.Row():
            result_output = gr.Markdown(label="分析结果")

        # 绑定事件
        analyze_btn.click(
            analyze_product,
            inputs=product_input,
            outputs=result_output
        )

        gr.Markdown("---")
        gr.Markdown("""
        ### 📋 使用说明
        1. 输入您想分析的产品名称
        2. 点击"开始分析"按钮
        3. 查看分析结果

        **注意**: 这是基础版本。完整分析功能需要配置Google AI API密钥。
        """)

    return app

def main():
    """主函数"""
    print("🎯 ProductScout AI 启动器")
    print("=" * 50)

    # 检查依赖
    if not check_and_install_requirements():
        print("❌ 依赖安装失败，无法启动应用")
        return 1

    # 创建应用
    try:
        app = create_minimal_app()
        print("✅ 应用创建成功")
    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # 启动应用
    try:
        print("\n🚀 启动Gradio应用...")
        print("📍 本地地址: http://localhost:7860")
        print("🔧 按Ctrl+C停止服务")
        print("-" * 50)

        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=True,
            quiet=False
        )

    except KeyboardInterrupt:
        print("\n👋 服务已停止")
        return 0
    except Exception as e:
        print(f"❌ 应用启动失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())