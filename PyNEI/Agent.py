"""NARS智能体「NARSAgent」的实现，旨在减少游戏与NARS本体的耦合
- 构造一个抽象的智能体系统
- 上接游戏代码，下接外部程序
"""

import random  # 用于babble

from PyNEI.Program import NARSType, NARSProgram  # 同路径相对导入使用「.文件名」
from PyNEI.Elements import *



class NARSAgent:
    """关于NARS功能的接口：抽象于「游戏本体」到「纳思本体」的「中间接口」

    主要功能：
    - 实现一个与「游戏环境」沟通的「通用框架」
        - 注册操作
        - 注册感知
        - 统一管理纳思元素：词项、操作、语句
            - 不随具体实现而变化
    - 将「具体纳思对接」与「通用纳思行动」区分开来
        - 不聚焦具体怎样调用命令
        - 不聚焦如何「注入语句」「获取回应」
    """

    # nars_type: 'opennars' or 'ONA'
    def __init__(self, nars_type: NARSType = None, rootPath: str = '.', mainGoal: str = None, mainGoal_negative: str = None):
        "构造方法"
        # 使用字典记录操作，并在后面重载「__getitem__」方法实现快捷读写操作
        # 空字典：获取这个操作「被程序发送了多少次」
        self._operation_container: dict[NARSOperation:int] = dict()
        # 使用列表处理感知器
        self._sensors: list[NARSSensor] = []  # 空列表
        # 使用「对象复合」的形式，把「具体程序启动」的部分交给「NARSProgram」处理
        self.brain: NARSProgram = None
        self.enable_brain_control: bool = True  # 决定是否「接收NARS操作」
        self.enable_brain_sense: bool = True  # 决定是否「接收外界感知」
        nars_type and self.equip_brain(
            nars_type, rootPath)  # 若未输入nars_type，也可以后续再初始化
        # 定义自身的「总目标」
        self.mainGoal: str = mainGoal
        self.mainGoal_negative: str = mainGoal_negative
        # 感知相关
        self._total_sense_inputs: int = 0  # 从外界获得的感知输入量
        # 操作相关
        self._total_initiative_operates: int = 0  # 从NARS程序接收的操作总数

    def __del__(self) -> None:
        "析构函数"
        self.disconnect_brain()

    # 程序实现相关 #

    @property
    def has_brain_equipped(self):
        "获取自己是否有「初始化大脑」"
        return self.brain != None

    def equip_brain(self, nars_type: NARSType, rootPath: str = '.'):  # -> NARSProgram
        "（配合disconnect可重复使用）装载自己的「大脑」：上载一个NARS程序，使得其可以进行推理"
        # 定义自身用到的「NARS程序」类型
        self.type: NARSType = nars_type
        if self.brain:  # 已经「装备」则报错
            raise "Already equipped a program!"
        self.brain: NARSProgram = NARSProgram.fromType(
            type=nars_type,
            rootPath=rootPath,
        )
        # 遇到「截获的操作」：交给专门函数处理
        self.brain.out_hook = self._handle_out_line
        # 启动大脑
        self.brain.launch()

    def disconnect_brain(self):
        "与游戏「解耦」，类似「断开连接」的作用"
        self.brain and self.brain.terminate()  # 终止程序运行
        self.brain = None  # 空置，以便下一次定义

    # update sensors (object positions), remind goals, and make inference
    def update(self, *sense_args: tuple, **sense_targets: dict):
        "NARS在环境中的行动：感知更新→目标提醒→推理步进"
        self.update_sensors(*sense_args, **sense_targets)
        # 原「remind_goal」：时刻提醒智能体要做的事情
        self.mainGoal and self.put_goal(self.mainGoal)
        self.mainGoal_negative and self.put_goal(
            self.mainGoal_negative, True)  # 时刻提醒智能体*不要做*的事情
        self._inference_step()

    # 语句相关 #

    def _inference_step(self) -> None:
        "通用模块：让NARS体「思考一个周期」"
        return self.brain.update_inference_cycles()

    # 感知相关 #
    def update_sensors(self, *sense_args: tuple, **sense_targets: dict):
        "其它特性留给后续继承"
        # 遍历所有感知器，从感知器统一获得感知
        for sensor in self._sensors:
            if sensor.enabled:  # 仅当感知器启用时遍历
                # 遍历获得的所有「感知」
                for perception in sensor(*sense_args, **sense_targets):
                    self.add_perception(perception)

    def add_perception(self, perception: NARSPerception) -> None:
        "统一添加感知：传递给「大脑」+计数"
        if self.enable_brain_sense:  # 需要启用「大脑感知」
            self.brain.add_perception(perception=perception)
            self._total_sense_inputs += 1  # 计数

    def add_sensor(self, sensor: NARSSensor):
        "注册感知器"
        self._sensors.append(sensor)

    def del_sensor(self, sensor: NARSSensor):
        "移除感知器"
        self._sensors.remove(sensor)

    @property
    def total_senses(self) -> int:
        "获取从外界获得的感知次数"
        return self._total_sense_inputs

    @property
    def num_cached_cmds(self) -> int:
        return self.brain.num_cached_inputs

    def clear_cached_cmds(self) -> None:
        "清除自身「大脑」缓存的命令"
        return self.brain.clear_cached_inputs()

    # 目标相关 #
    def put_goal(self, goalName: str, is_negative: bool = False):
        "向智能体置入目标（带名称） TODO 不要带negative到具体程序实现中"
        return self.brain.put_goal(goalName=goalName, is_negative=is_negative)

    def praise_goal(self, goalName: str):
        "（现仅负责传递至brain）让智能体感到「目标被实现」，亦即「奖励」"
        return self.brain.praise_goal(goalName=goalName)

    def punish_goal(self, goalName: str):
        "（现仅负责传递至brain）让智能体感到「目标未实现」，亦即「惩罚」"
        return self.brain.punish_goal(goalName=goalName)

    # 操作相关 #
    def __getitem__(self, operation: NARSOperation) -> int:
        "获取自身「是否要进行某个操作」（返回bool）"
        return self._operation_container.get(operation.name, 0)  # 默认0

    def __setitem__(self, operation: NARSOperation, value: int):
        "设置自身「需要有哪些操作」"
        self._operation_container[operation.name] = int(value)

    def __contains__(self, operation: NARSOperation):
        "获取「操作是否被定义过」"
        return self._operation_container.__contains__(operation.name)

    def __iter__(self):
        "枚举自身的「所有操作」"
        return {  # 保证遍历出来的是操作
            name: NARSOperation(name)
            for name in self._operation_container
        }.__iter__()  # 返回字典的迭代器

    def reset_stored_operations(self, value: int = 0):
        "重置已存储的操作"
        for oname in self._operation_container:
            self._operation_container[oname] = value

    def register_basic_operation(self, operation: NARSOperation):
        return self.brain.register_basic_operation(operation=operation)

    def register_basic_operations(self, *operations: list[NARSOperation]):
        return [
            self.register_basic_operation(operation=operation)
            for operation in operations
        ]

    def _handle_out_line(self, line: str):  # get operations
        # 从一行语句中获得操作
        if self.brain and self.brain.out_hook and (operation_name := self.brain.catch_operation_name(line)):
            self.handle_program_operation(
                NARSOperation(operation_name)  # 从字符串到操作（打包）
            )  # 传递一个「纳思操作」

    def handle_program_operation(self, operation: NARSOperation):
        "对接命令行与游戏：根据NARS程序返回的操作字符串，存储相应操作"
        if self.enable_brain_control:  # 需要启用「大脑操作」
            self.store_operation(operation)  # 存储操作
            self._total_initiative_operates += 1  # 增加接收的操作次数

    @property
    def need_babble(self) -> bool:
        "反应NARS是否需要最初的babble"
        return self.brain.enable_babble

    def babble(self, probability: int = 1, operations=[], force_operation: bool = True):
        "随机行为，就像婴儿的牙牙学语（有概率）"  # 🆕为实现「与具体实现程序形式」的分离，直接提升至Agent层次
        if not probability or random.randint(1, probability) == 1:  # 几率触发
            self.force_unconscious_operation(
                random.choice(operations),  # 随机取一个NARS操作
                force_operation  # 一定要做出操作吗？
            )  # 相当于「强制无意识操作」

    def force_unconscious_operation(self, operation: NARSOperation, force_operation: bool = True):
        "强制「无意识操作」：让智能体执行，仅告诉NARS程序「我执行了这个操作」"
        self.brain.put_unconscious_operation(operation=operation)
        force_operation and self.store_operation(operation)  # 智能体：执行操作

    def store_operation(self, operation: NARSOperation):
        "存储对应操作，更新自身状态"
        self[operation] += 1  # 直接设置对应「要执行的操作」为真

    @property
    def stored_operation_dict(self) -> dict[NARSOperation:int]:
        "获取自己存储的操作字典（复制新对象）"
        return self._operation_container.copy()  # 一个新字典

    @property
    def stored_operation_names(self):
        "获取自己存储的所有操作名（迭代器）"
        return self._operation_container.keys()  # 一个新字典

    @property
    def active_operation_names(self):
        "获取被激活的操作（迭代器）"
        return (
            operation
            for operation, activeNum in self._operation_container.items()
            if activeNum > 0
        )

    @property
    def total_operates(self) -> int:
        "获取从「NARS计算机实现」中截获的操作次数"
        return self._total_initiative_operates
