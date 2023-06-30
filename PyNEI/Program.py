"""有关NARS智能体(NARSAgent)与CIN(Computer Implement of NARS)的通信

前身：Boyang Xu, *NARS-FighterPlane*

类の概览
- NARSType: 注册已有的CIN类型
- NARSProgram：抽象一个CIN通信接口
"""

import threading # 用于打开线程
import queue
import subprocess # 用于打开进程
import signal # 用于终止程序

from enum import Enum # 枚举NARS类型

# ⚠使用「包.路径」导入，是默认Python包的做法
from PyNEI.Elements import * # 📌注：模块下使用相对路径「.」导入当前路径下的模块（VSCode调试下）

DEBUG:bool = False

"""NARS具体实现的「类型」
记录NARS具体实现时调用的类型
"""
class NARSType(Enum):
    
    OPENNARS:str = 'opennars'
    ONA:str = 'ONA'
    ONA_OLD:str = 'ONA_old'
    PYTHON:str = 'python'
    
    @staticmethod
    @property
    def values() -> list[str]:
        return [t.value for t in NARSType]

"""具体与纳思通信的「程序」
核心功能：负责与「NARS的具体计算机实现」沟通
- 例：封装好的NARS程序包（支持命令行交互
"""
class NARSProgram:
    
    # NAL内置对象区 #
    
    '表示「自我」的对象'
    _TERM_SELF:str = '{%s}' % NARSPerception.OBJECT_SELF # 嵌入「自我」词项（必须是{专名}的形式）
    
    # NAL语句模板区 #
    
    '指示「某个对象有某个状态」'
    SENSE_TEMPLETE:str = '<{%s} --> [%s]>. :|:'

    '指示「自我正在执行某操作」（无意识操作 Babble）'
    BABBLE_TEMPLETE:str = f'<(*,{_TERM_SELF}) --> ^%s>. :|:' # 注意：是操作的名字
    
    '指示「自我需要达到某个目标」'
    GOAL_TEMPLETE:str = f'<{_TERM_SELF} --> [%s]>! :|:' # ？是否一定要一个「形容词」？
    GOAL_TEMPLETE_NEGATIVE:str = f'(--, <{_TERM_SELF} --> [%s]>)! :|:' # 一个「负向目标」，指导「实现其反面」
    
    '指示「某目标被实现」'
    PRAISE_TEMPLETE:str = f'<{_TERM_SELF} --> [%s]>. :|:'
    
    '指示「某目标未实现」'
    PUNISH_TEMPLETE:str = f'(--,<{_TERM_SELF} --> [%s]>). :|:'
    
    '指示「自我有一个可用的（基本）操作」（操作注册）'
    OPERATION_REGISTER_TEMPLETE:str = BABBLE_TEMPLETE # 暂时使用Babble的模板
        
    # 程序构造入口 #
    
    @staticmethod
    def fromType(type:NARSType, rootPath:str='.', out_hook=None):
        """从NARSType中自动构造CIN对象
        - 可配置根目录，exe名字使用默认值以简化工作
        - 其调用格式要求下属NARSType必须有特定参数格式：
            - 首个位置参数为「可执行文件路径」
            - 可选参数out_hook
        """
        cls, app_name = TYPE_CIN_DICT[type] # 从字典获取
        return cls(f'{rootPath}\\%s' % app_name, out_hook=out_hook) # 用类构造函数（确保第一个参数是可执行文件路径）
        # Windows路径使用反斜杠
    
    # 程序/进程相关 #
    
    def __init__(self, out_hook=None):
        "初始化NARS程序：启动命令行、连接「NARS计算机实现」、启动线程"
        "推理循环频率"
        self.inference_cycle_frequency:int = 1  # set too large will get delayed and slow down the game
        "存储CIN直接输出的钩子：捕捉一切命令行输出"
        self.out_hook = out_hook
        self._cached_inputs:list[str] = [] # 定义一个先进先出队列，存储待写入的指令
        
    @property
    def type(self) -> NARSType:
        "获取自身（直接）所属的NARS类型"
        return TYPE_CIN_DICT.get(self.__class__, None)
    
    def launch(self):
        "（API）功能分离：启动NARS程序"
        pass
    
    def terminate(self):
        """（API）终止程序"""
        pass

    # 用析构函数替代「process_kill」方法
    def __del__(self):
        "程序结束时，自动终止NARS"
        self.terminate()
    
    # 语句相关 #
    
    # 语句
    def add_input(self, sentense:str) -> None:
        "（API）以字符串形式注入NAL语句"
        pass
    
    def add_inference_cycles(self, num:int):
        "（API）推理循环步进"
        pass
    
    def update_inference_cycles(self) -> None:
        "更新自身推理循环"
        self.inference_cycle_frequency and self.add_inference_cycles(self.inference_cycle_frequency)
    
    @property
    def num_cached_inputs(self) -> int:
        "返回缓存（待输入进NARS）的命令数量"
        return len(self._cached_inputs)
    
    def clear_cached_inputs(self) -> None:
        "强制清除命令缓存"
        return self._cached_inputs.clear()
    
    # 感知
    def add_perception(self, perception:NARSPerception) -> None:
        "（API）统一添加感知"
        pass
    
    # 目标
    def put_goal(self, goalName:str, is_negative:bool = False):
        "（API）向智能体置入目标（以NAL语句的形式）"
        pass
    
    def praise_goal(self, goalName:str):
        "（API）让智能体感到「目标被实现」，亦即「奖励」"
        pass
    
    def punish_goal(self, goalName:str):
        "（API）让智能体感到「目标未实现」，亦即「惩罚」"
        pass

    @property
    def enable_babble(self) -> bool:
        "是否支持Babble"
        return bool(self.__class__.BABBLE_TEMPLETE)
    
    def put_unconscious_operation(self, operation:NARSOperation):
        "（API）强制「无意识操作」：告诉NARS程序「我执行了这个操作」"
        pass
    
    def register_basic_operation(self, operation:NARSOperation):
        "（API）注册「基础操作」：告诉NARS程序「我可以执行这个操作」"
        pass


class Cmdline(NARSProgram):
    """抽象类：所有用命令行实现的CIN
    - 使用一个子进程，运行CIN主程序
    - 使用两个子线程，分别执行CIN进程的I/O任务
    """
    
    def __init__(self, out_hook=None):
        """初始化"""
        super().__init__(out_hook)
    
    def launch(self):
        "功能分离：启动NARS程序"
        self._launch_CIN()
        self._launch_thread_read()
        self._launch_thread_write()
    
    # 进程相关 #
    
    def terminate(self):
        """终止程序 TODO：似乎未能正确关闭，会报错"""
        try:
            self.process.send_signal(signal.CTRL_C_EVENT)
            self.process.terminate()
            self.process = None # 空置
        except BaseException as e:
            print(f'Failed to terminate process: {e}')
    
    def _launch_CIN(self):
        """并行启动CIN
        使用cmd形式打开子进程，并根据NARS类型启动对应程序（适用于命令行打开的程序）
        创建一个子进程来执行 ls -l 命令，并将标准输出和错误输出捕获到 output 和 error 变量中。
            母进程可以继续执行其他任务，而不会被阻塞，直到需要获取子进程输出的时候再调用 process.communicate()
        """
        self.process = subprocess.Popen(
            ["cmd"], # 使用CMD打开
            bufsize=1,
            stdin=subprocess.PIPE, # 输入管道
            stdout=subprocess.PIPE, # 输出管道
            universal_newlines=True,  # convert bytes to text/string
            shell=False
        )
        self.launch_program() # 「具体启动程序」交给剩下的子类实现
        self.write_line('*volume=0')
        
    def launch_program(self):
        "直接启动程序"
        pass
    
    def _launch_thread(self, target, args) -> threading.Thread:
        "通用：开启线程（返回开启的线程）"
        self.read_line_thread = threading.Thread(
            target = target,
            args = args
        )

        # 将线程设置为守护线程，即在程序退出时自动终止线程
        self.read_line_thread.daemon = True
        
        # 启动线程
        self.read_line_thread.start()

    def _launch_thread_read(self):
        "开启子线程，负责接收NARS程序的输出"
        # 创建线程对象 self.read_line_thread
        self.read_line_thread = self._launch_thread(
            target=self.read_line, # 目标函数是 self.read_line
            args=(self.process.stdout,) # 将 self.process.stdout 作为参数传递给 self.read_line 方法
        )

    def _launch_thread_write(self):
        "解决「写入卡顿」的方案：开启子线程，负责NAL语句的异步写入"
        # 创建线程对象 self.write_line_thread
        self.write_line_thread = self._launch_thread(
            target=self.async_write_lines, # 目标函数是 self.write_line
            args=(self.process.stdin,) # 将 self.process.stdout 作为参数传递给 self.write_line 方法
        )

    # 语句相关 #
    
    # 语句
    def add_input(self, sentense:str) -> None:
        "置入NAL语句 实现：向命令行添加命令"
        self.process.stdin.write(sentense + '\n') # ⚠注：写入命令可能会在这里卡顿，主进程可能因此被阻塞
        self.process.stdin.flush()
        # print(f'write: {sentense}')
    
    def add_inference_cycles(self, num:int):
        "推理循环步进"
        self.process.stdin.write(f'{num}\n')
        self.process.stdin.flush()
    
    def update_inference_cycles(self) -> None:
        "更新自身推理循环"
        if self.inference_cycle_frequency: # 若大于零
            self.add_inference_cycles(self.inference_cycle_frequency)
    
    # 感知
    def add_perception(self, perception:NARSPerception) -> None:
        "统一添加感知"
        self.write_line(
            self.__class__.SENSE_TEMPLETE % (perception.object, perception.adjective) # 套模板
        )
    
    # 目标
    def put_goal(self, goalName:str, is_negative:bool = False):
        "向智能体置入目标（以NAL语句的形式）"
        self.write_line(
            (
                self.__class__.GOAL_TEMPLETE_NEGATIVE # 根据不同类的常量决定模板
                if is_negative
                else self.__class__.GOAL_TEMPLETE
            ) % goalName
        )
    
    def praise_goal(self, goalName:str):
        "让智能体感到「目标被实现」，亦即「奖励」"
        self.write_line(self.__class__.PRAISE_TEMPLETE % goalName)
    
    def punish_goal(self, goalName:str):
        "让智能体感到「目标未实现」，亦即「惩罚」"
        self.write_line(self.__class__.PUNISH_TEMPLETE % goalName)

    @property
    def enable_babble(self) -> bool:
        return bool(self.__class__.BABBLE_TEMPLETE)
    
    def put_unconscious_operation(self, operation:NARSOperation):
        "强制「无意识操作」：告诉NARS程序「我执行了这个操作」"
        if self.__class__.BABBLE_TEMPLETE and (
            sentence := (self.__class__.BABBLE_TEMPLETE % operation.name)
        ):
            self.write_line(sentence) # 置入「自己在进行什么操作」
    
    def register_basic_operation(self, operation:NARSOperation):
        "注册「基础操作」：告诉NARS程序「我可以执行这个操作」"
        if self.__class__.OPERATION_REGISTER_TEMPLETE and (
            sentence := (self.__class__.OPERATION_REGISTER_TEMPLETE % operation.name)
        ):
            self.write_line(sentence) # 置入「自己在进行什么操作」
    
    # 运行时相关 #

    def read_line(self, out): # read line without blocking
        "读取程序的（命令行）输出"
        for line in iter(out.readline, b'\n'):
            self.out_hook(line) # 传递单个输出行到指定外接钩子
        out.close() # 关闭输出流
    
    def catch_operation_name(self, line:str):
        "（API）从输出的一行（语句）中获取信息，并返回截取到的「操作字符串」"
        pass
    
    def async_write_lines(self, stdin):
        "从自身指令缓冲区中读取输入，送入程序的stdin中"
        while self.process != None: # 始终运行，读取缓冲区中的指令列表
            if self._cached_inputs:
                cmd:str = self._cached_inputs.pop(0) # 取最开头（pop(0)代替shift）
                self.add_input(cmd) # 异步调用（不阻塞主进程）
                if (n_cmds:=self.num_cached_inputs) > 0xff:
                    print(
                        f"Warning: The number of cached commands has exceeded the limit with n={n_cmds}!",
                        f'> Last cmd is: {cmd}', sep='\n'
                    )

    # @measure_time
    def write_line(self, cmd:str):
        "缓存命令到缓冲区中"
        DEBUG and print(f'add {cmd} to {self.num_cached_inputs}')
        self._cached_inputs.append(cmd) # 存入缓冲区
        return # 代码删除后记：不适宜「对每个输入的语句都开一个新线程」，对系统占用的开销太大


class OpenNARS(Cmdline):
    """Java版实现：OpenNARS
    """
    
    "可执行文件路径"
    DEFAULT_JAR_NAME:str = r'opennars.jar'
    
    # 特有语法区 #
    
    PUNISH_TEMPLETE = f'<{NARSProgram._TERM_SELF} --> [%s]>. :|: %%0%%' # opennars' grammar（避免百分号歧义）
    
    def launch_program(self):
        super().launch_program()
        # OpenNARS的实现
        self.add_input(f'java -Xmx1024m -jar {self.jar_path}')  # self.add_input('java -Xmx2048m -jar opennars.jar')
    
    def __init__(self, jar_path:str = f'./{DEFAULT_JAR_NAME}', out_hook=None):
        self.jar_path = jar_path
        super().__init__(out_hook=out_hook)
        self.inference_cycle_frequency = 5

    def catch_operation_name(self, line:str) -> str:
        if line[0:3] == 'EXE': # 若为操作前缀
            subline = line.split(' ', 2)[2] # 获取EXE后语句
            # print(subline) # 操作文本：「EXE ^right([{SELF}])=null」
            return subline.split('(', 1)[0][1:] # 避免'^^opera'


class ONA(Cmdline):
    """C实现：OpenNARS for Application
    """
    
    "可执行文件路径"
    DEFAULT_EXE_NAME:str = 'NAR.exe'
    DEFAULT_EXE_NAME_OLD:str = 'NAR_old.exe'
    
    # 特有语法区 #
    
    BABBLE_TEMPLETE:str = None # ONA Babble 无效：语句「<(*,{SELF}) --> ^deactivate>. :|:」报错「OSError: [Errno 22] Invalid argument」
    
    PUNISH_TEMPLETE = f'<{NARSProgram._TERM_SELF} --> [%s]>. :|: {"{0}"}' # ONA's grammar （注：这里使用「{"{0}"}」避免字符串歧义）
    
    OPERATION_REGISTER_TEMPLETE:str = f'(*,{NARSProgram._TERM_SELF}, ^%s). :|:' # 操作注册
    
    def __init__(self, exe_path:str = f'.\\{DEFAULT_EXE_NAME}', out_hook=None):
        self.exe_path = exe_path
        super().__init__(out_hook=out_hook)
        self.inference_cycle_frequency = 0 # ONA会自主更新
    
    def launch_program(self):
        super().launch_program()
        # ONA的实现
        self.add_input(f'{self.exe_path} shell')

    def catch_operation_name(self, line:str) -> str:
        if (line[0:1] == '^'): # 避免在退出游戏时出错
            # print(line) # 操作文本：「EXE ^right executed with args」
            return line.split(' ', 1)[0][1:] # 避免'^^opera'


class Python(Cmdline):
    """Python实现：NARS Python
    """
    
    "程序路径"
    DEFAULT_EXE_NAME:str = r'main.exe'
    
    # 特定模板 # 注：NARS-Python 对语句使用圆括号
    
    '指示「某个对象有某个状态」'
    SENSE_TEMPLETE:str = '({%s} --> [%s]). :|:'

    '指示「自我正在执行某操作」（无意识操作 Babble）'
    BABBLE_TEMPLETE:str = f'((*, {NARSProgram._TERM_SELF}) --> %s). :|:' # 移植自NARS-Pong
    
    '指示「自我需要达到某个目标」'
    GOAL_TEMPLETE:str = f'({NARSProgram._TERM_SELF} --> [%s])! :|:' # ？是否一定要一个「形容词」？
    GOAL_TEMPLETE_NEGATIVE:str = f'({NARSProgram._TERM_SELF} --> (-, [%s]))! :|:' # 语法来自NARS Python
    
    '指示「某目标被实现」'
    PRAISE_TEMPLETE:str = f'({NARSProgram._TERM_SELF} --> [%s]). :|:'
    
    '指示「某目标未实现」'
    PUNISH_TEMPLETE:str = f'({NARSProgram._TERM_SELF} --> [%s]). :|: %%0.00;0.90%%'
    
    OPERATION_REGISTER_TEMPLETE:str = f'((*, {NARSProgram._TERM_SELF}) --> %s). :|:'
    
    # 类实现 #
    
    def __init__(self, exe_path:str = f'.\\{DEFAULT_EXE_NAME}', out_hook=None):
        self.exe_path = exe_path
        super().__init__(out_hook=out_hook)
        self.inference_cycle_frequency = 0 # NARS-Python 不需要更新（暂时只能输入NAL语句）
    
    def launch_program(self):
        super().launch_program()
        # NARS Python实现
        self.add_input(f'{self.exe_path}')

    def catch_operation_name(self, line:str) -> str:
        if 'reject' in line.lower():
            print(f'Reject: {line}')
        if 'EXE' in line: # 若为操作前缀
            # print(f'{line}') # 操作文本：「EXE: ^left based on desirability: 0.9」
            return line.split(' ', 2)[1][1:]

TYPE_CIN_DICT:dict[NARSType:tuple[type, str]] = {
    NARSType.OPENNARS: (OpenNARS, OpenNARS.DEFAULT_JAR_NAME),
    NARSType.ONA: (ONA, ONA.DEFAULT_EXE_NAME),
    NARSType.ONA_OLD: (ONA, ONA.DEFAULT_EXE_NAME_OLD),
    NARSType.PYTHON: (Python, Python.DEFAULT_EXE_NAME),
}
TYPE_CIN_DICT.update({
    v[0]: k # 添加「类→NARSType」的映射
    for k,v in TYPE_CIN_DICT.items()
})