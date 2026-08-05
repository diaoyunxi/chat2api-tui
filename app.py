# 在文件头部导入 config
from core import config
import cmd
class ChatCLI(cmd.Cmd):
    # ...
    def __init__(self):
        super().__init__()
        self.llm = LLMClient()
        self.tool_loader = ToolLoader()
        self.agent = Agent(self.llm, self.tool_loader)
        self.conv = Conversation()
        self.current_image_path = None
        self.use_stream = False
        # 从配置读取默认模型
        self.model = config.get("default_model", "deepseek-v4-flash")
        self.supported_models = config.get("supported_models", ["deepseek-v4-flash", "deepseek-v4-pro"])

    def do_model(self, arg):
        """切换模型"""
        if not arg:
            print(f"当前模型: {self.model}")
            return
        if arg in self.supported_models:
            self.model = arg
            print(f"✅ 已切换到模型: {self.model}")
        else:
            print(f"❌ 支持的模型: {', '.join(self.supported_models)}")
