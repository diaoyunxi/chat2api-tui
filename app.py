#!/usr/bin/env python
"""
Chat2API 命令行客户端（简化版）
支持多模态、工具热加载、智能体循环、对话持久化、模型切换
命令以 / 开头，普通输入作为消息发送
"""
import cmd
import os

from core.llm_client import LLMClient
from core.tool_loader import ToolLoader
from core.conversation import Conversation
from agent import Agent
from core import config


class ChatCLI(cmd.Cmd):
    intro = """
╔══════════════════════════════════════════════════════════╗
║  🤖 Chat2API 智能体客户端                              ║
║  输入消息直接对话  |  /help 查看命令                   ║
╚══════════════════════════════════════════════════════════╝
"""
    prompt = "你> "

    def __init__(self):
        super().__init__()
        self.llm = LLMClient()
        self.tool_loader = ToolLoader()
        self.agent = Agent(self.llm, self.tool_loader)
        self.conv = Conversation()
        self.current_image_path: str | None = None
        self.use_stream = False
        # 从配置读取默认模型
        self.model = config.get("default_model", "deepseek-v4-flash")
        self.supported_models = config.get("supported_models", ["deepseek-v4-flash", "deepseek-v4-pro"])
        self.conv = Conversation()
        self.conv.system_prompt = (
            "你是一个具备调用工具能力的AI助手。\n"
            "可用工具：read_file, write_file, exec_cmd, ask_user。\n"
            "当用户请求执行命令、读写文件或需要向用户提问时，你必须使用对应的工具，\n"
            "并且严格按照函数调用的标准格式（tool_calls）来调用，不要自行输出JSON或模拟结果。\n"
            "你的回答应基于工具返回的真实数据。"
        )

    # ---------- 核心交互 ----------
    def default(self, line: str):
        """非命令输入均视为发送消息"""
        if not line.strip():
            return
        # 如果有附加图片，构建多模态消息
        if self.current_image_path:
            msg = LLMClient.build_multimodal_message(line, image_path=self.current_image_path)
            self.conv.messages.append(msg)
            print(f"🖼️  已附加图片: {os.path.basename(self.current_image_path)}")
            self.current_image_path = None
        else:
            self.conv.add_message("user", line)

        # 显示用户消息
        print(f"\n👤 你: {line}")

        # 调用智能体，传入当前模型
        try:
            print("🤖 AI: ", end="", flush=True)
            response = self.agent.run(self.conv, model=self.model)
            print(response)
        except Exception as e:
            print(f"\n❌ 错误: {str(e)}")

    # ---------- 命令 ----------
    def do_new(self, arg):
        """新对话 (丢弃当前)"""
        if self.conv.messages:
            self.conv.save()  # 自动保存旧对话
        self.conv = Conversation()
        self.current_image_path = None
        print("✅ 已创建新对话")

    def do_save(self, arg):
        """保存当前对话"""
        self.conv.save()
        print(f"✅ 已保存: {self.conv.id}")

    def do_load(self, arg):
        """加载对话: /load <对话ID>   (不带参数则列出所有)"""
        if not arg:
            files = Conversation.list_conversations()
            if not files:
                print("📭 没有历史对话")
                return
            print("📚 历史对话列表:")
            for f in files:
                print(f"  {f.replace('.json', '')}")
            return
        # 加载指定ID
        filepath = f"data/conversations/{arg}.json"
        if not os.path.exists(filepath):
            print(f"❌ 对话 {arg} 不存在")
            return
        self.conv = Conversation.load(filepath)
        self.current_image_path = None
        print(f"✅ 已加载对话: {arg}")
        self.show_history()

    def do_system(self, arg):
        """设置系统提示词: /system <提示词>"""
        if not arg:
            print(f"当前系统提示: {self.conv.system_prompt or '(无)'}")
        else:
            self.conv.system_prompt = arg
            print("✅ 系统提示词已更新")

    def do_image(self, arg):
        """附加图片: /image <图片路径>"""
        if not arg:
            print("当前附加图片: " + (os.path.basename(self.current_image_path) if self.current_image_path else "无"))
            return
        if not os.path.exists(arg):
            print(f"❌ 文件不存在: {arg}")
            return
        self.current_image_path = arg
        print(f"🖼️  已附加图片: {os.path.basename(arg)}")

    def do_reload(self, arg):
        """热加载工具 (无需重启)"""
        self.tool_loader.reload()
        print("✅ 工具已重载")

    def do_history(self, arg):
        """显示当前对话历史"""
        self.show_history()

    def do_stream(self, arg):
        """切换流式输出 (on/off)"""
        if arg.lower() in ("on", "true", "1"):
            self.use_stream = True
            print("✅ 流式输出已开启（实验性）")
        else:
            self.use_stream = False
            print("✅ 流式输出已关闭")

    def do_model(self, arg):
        """切换模型: /model <模型名> 或不带参数查看当前"""
        if not arg:
            print(f"当前模型: {self.model}")
            return
        if arg in self.supported_models:
            self.model = arg
            print(f"✅ 已切换到模型: {self.model}")
        else:
            print(f"❌ 支持的模型: {', '.join(self.supported_models)}")

    def do_exit(self, arg):
        """退出程序 (自动保存)"""
        if self.conv.messages:
            self.conv.save()
        print("👋 再见！")
        return True

    def do_help(self, arg):
        """显示帮助"""
        print("""
╔══════════════════════════════════════════════════════════╗
║  可用命令:                                             ║
║  /new         - 新对话 (自动保存旧对话)                 ║
║  /save        - 保存当前对话                           ║
║  /load [id]   - 列出所有对话 或 加载指定ID             ║
║  /system [文本] - 查看或设置系统提示词                  ║
║  /image [路径] - 附加图片用于多模态分析                ║
║  /reload      - 热加载 tools/ 目录下的工具             ║
║  /history     - 显示当前对话历史                       ║
║  /stream on/off - 切换流式输出 (实验性)               ║
║  /model [pro|flash] - 切换模型 (默认flash)             ║
║  /exit        - 退出                                   ║
║  /help        - 显示本帮助                             ║
║                                                       ║
║  直接输入文本即为发送消息，智能体会自动调用工具。     ║
╚══════════════════════════════════════════════════════════╝
""")

    # ---------- 辅助 ----------
    def show_history(self):
        """打印对话历史"""
        if not self.conv.messages:
            print("📭 当前对话为空")
            return
        print("📜 对话历史:")
        for msg in self.conv.messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if role == "user":
                print(f"  👤 你: {content}")
            elif role == "assistant":
                print(f"  🤖 AI: {content}")
            elif role == "tool":
                print(f"  🔧 工具: {content[:80]}...")
            elif role == "system":
                print(f"  ⚙️ 系统: {content}")

    def emptyline(self):
        pass

    def do_EOF(self, arg):
        print()
        return self.do_exit(arg)


if __name__ == "__main__":
    try:
        ChatCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n👋 退出")