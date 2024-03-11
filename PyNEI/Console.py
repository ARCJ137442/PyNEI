"""CIN(NARS计算机实现)的命令行窗口
集成一些CIN的命令行模式
"""
# from os import getcwd
# print(getcwd())
from PyNEI.Program import NARSType, NARSProgram  # 同路径相对导入使用「.文件名」


class NARSConsole():
    """命令行接口类
    用于创建NARSProgram，与CIN进行间接交互
    """

    def __init__(self, type: NARSType, rootPath: str, asyncOut: bool = False, inputPrompt: str = "input: ") -> None:
        self.program: NARSProgram = NARSProgram.fromType(
            type=type,  # CIN类型
            rootPath=rootPath,  # 可执行文件的根路径
            out_hook=self._out_hook  # 默认钩子
        )

        "决定是否要启用缓冲区进行「同步输出」，否则在接收到程序输出时直接输出"
        self.async_out: bool = asyncOut

        "输出缓冲区：用于「异步⇒同步」处理输出，让程序自行决定输出处理时间"
        self._out_buffer: list[str] = []

        "决定请求用户输入的提示词"
        self.input_prompt: str = inputPrompt

    def launch(self):
        "真正开始启动"
        # 启动CIN
        self.program.launch()

        # 注：在此处才开始连接钩子，阻止cmd启动的输出，例如：「(c) Microsoft Corporation。保留所有权利。」
        self.program.out_hook = self._out_hook

        # 进入命令行模式
        self._console()

    def _console(self):
        "开启命令行模式"
        # self.program.add_to_cmd('\n'*4) # 直接添加进命令行
        # self.program.add_to_cmd('\n') # 直接添加进命令行
        # self.program.add_to_cmd('\n') # 直接添加进命令行
        self._clear_out_buffer()  # 清除cmd启动时、CIN启动前的输出
        while True:
            try:
                # 遍历处理输出（同步）
                if not self.async_out:
                    for out_line in self._out_buffer:
                        self.handle_out_line(line=out_line)
                    self._clear_out_buffer()  # 清除缓冲
                # 处理输入
                if inp := input(self.input_prompt):
                    # 注：无需对数字「推理步骤」进行特殊识别，其效果与直接在命令行输入等价
                    self.program.add_input(inp + '\n')  # 直接添加进命令行，附加换行后缀
            except KeyboardInterrupt:  # Ctrl+C退出
                self.program.terminate()
                break

    def _out_hook(self, line: str) -> None:
        "处理NARSProgram的输出"
        return (
            self.handle_out_line  # 若为异步输出，则不存入
            if self.async_out else
            self._out_buffer.append  # 否则：向缓冲区中存入输出
        )(line)

    def _clear_out_buffer(self) -> None:
        "清除输出缓冲区"
        return self._out_buffer.clear()

    def handle_out_line(self, line: str) -> None:
        "真正处理输出"
        line and print(line)
