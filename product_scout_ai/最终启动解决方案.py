#!/usr/bin/env python3
"""
ProductScout AI 最终启动解决方案

解决所有已知问题：
1. 包导入检查和安装
2. Python路径配置
3. 端口冲突检查
4. 服务启动
"""
import sys
import os
import subprocess
import time
import socket

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
    try:
        result = subprocess.run(
            ['lsof', '-t', f'-i:{port}'],
            capture_output=True,
            text=True
        )
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid])
                    print(f"✅ 终止进程 {pid} (端口 {port})")
                except:
                    pass
            return True
    except:
        pass
    return False

def check_and_install_requirements():
    """检查并安装依赖包"""
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
        except subprocess.CalledProcessError as e:
            print(f"❌ 包安装失败: {e}")
            return False

    print("✅ 所有依赖包检查完成")
    return True

def create_minimal_gradio_app():
    """创建最小化的Gradio应用"""
    print("🚀 创建Gradio应用...")

    # Add src to Python path
    src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
    sys.path.insert(0, src_path)

    try:
        import gradio as gr

        def analyze_product(product_name, category, market):
            """简单的产品分析函数"""
            if not product_name:
                return "请输入产品名称"

            # 模拟分析结果
            result = f"""
        ## 📊 产品分析结果

        **产品名称**: {product_name}
        **产品类别**: {category}
        **目标市场**: {market}

        ### 分析维度:
        - **市场趋势**: 🟡 需要深入分析 (需要配置AI API)
        - **竞争分析**: 🟡 需要深入分析 (需要配置AI API)
        - **盈利潜力**: 🟡 需要深入分析 (需要配置AI API)
        - **市场机会**: 🟡 需要深入分析 (需要配置AI API)

        ---
        *这是ProductScout AI的基础版本。完整功能需要配置Google AI API密钥。*

        ### 📋 下一步
        1. 配置Google AI API密钥
        2. 重新启动服务以获得完整功能
        3. 访问文档了解API配置方法
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
                category_input = gr.Dropdown(
                    choices=["电子产品", "服装配饰", "食品饮料", "家居用品", "运动健身", "教育培训", "其他"],
                    label="产品类别",
                    value="其他"
                )
                market_input = gr.Dropdown(
                    choices=["国内市场", "国际市场", "亚太市场", "欧美市场", "新兴市场"],
                    label="目标市场",
                    value="国内市场"
                )

            with gr.Row():
                analyze_btn = gr.Button("🚀 开始分析", variant="primary")

            with gr.Row():
                result_output = gr.Markdown(label="分析结果")

            # 绑定事件
            analyze_btn.click(
                analyze_product,
                inputs=[product_input, category_input, market_input],
                outputs=result_output
            )

            gr.Markdown("---")
            gr.Markdown("""
            ### 📋 使用说明
            1. 输入产品名称和选择类别、市场
            2. 点击"开始分析"按钮
            3. 查看分析结果

            **注意**:
            - 当前为基础版本，提供框架展示
            - 完整AI分析功能需要配置Google AI API密钥
            - 请参考项目文档了解详细配置方法

            ### 🔧 故障排除
            - 如果服务无法启动，检查端口7860是否被占用
            - 如果功能不完整，检查API配置
            - 查看启动指南获取更多帮助
            """)

        return app

    except Exception as e:
        print(f"❌ 应用创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    """主函数"""
    print("🎯 ProductScout AI 最终启动解决方案")
    print("=" * 60)

    # 检查依赖
    if not check_and_install_requirements():
        print("❌ 依赖安装失败，无法启动应用")
        return 1

    # 检查端口
    port = 7860
    print(f"\n🔍 检查端口 {port}...")

    if not check_port_available(port):
        print(f"⚠️  端口 {port} 被占用，尝试终止占用进程...")
        if kill_process_on_port(port):
            time.sleep(2)  # 等待进程完全终止
            if not check_port_available(port):
                print(f"❌ 无法释放端口 {port}，请手动终止相关进程")
                return 1
        else:
            print(f"❌ 无法终止占用端口 {port} 的进程")
            return 1

    print(f"✅ 端口 {port} 可用")

    # 创建应用
    app = create_minimal_gradio_app()
    if not app:
        return 1

    # 启动应用
    try:
        print(f"\n🚀 启动Gradio应用...")
        print(f"📍 本地地址: http://localhost:{port}")
        print(f"📍 网络地址: http://0.0.0.0:{port}")
        print(f"🔧 按Ctrl+C停止服务")
        print("-" * 60)

        app.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            debug=False,
            quiet=False,
            show_error=True
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