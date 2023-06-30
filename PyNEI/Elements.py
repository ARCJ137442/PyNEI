"""有关NARS从「具体实现」中抽象出的元素集合

在不同CIN（NARS计算机实现）中，找到一个「共通概念」，用这些「共通概念」打造不同CIN的沟通桥梁

- Perception 感知
- Operation 操作
- Sensor 感知器
"""

"""抽象出一个「纳思操作」来
主要功能：记录其名字，并方便语法嵌入
TODO 后续可扩展：操作参数
"""
class NARSOperation(): # 现在不需要枚举类
    
    def __init__(self, name:str='') -> None:
        # 警惕「忘去除前缀」的现象
        if name[0] == '^':
            self.name = name[1:] # 去头
            print(f'Warning: mutiple "^" in name of operation {name}')
        else: # 否则默认设置
            self.name = name
    
    @property
    def value(self) -> any:
        "获取其值"
        return f'^{self.name}'
    
    def __eq__(self, other: object) -> bool:
        "相等⇔名称相等"
        return self.name == other.name
    
    def __repr__(self) -> str:
        return f"<NARS Operation {self.value}>"
    
    def __str__(self) -> str:
        "字符串就是其值"
        return self.value

"""抽象出一个「NARS感知」出来
主要功能：作为NARS感知的处理对象
- 记录其「主语」「表语」，且由参数**唯一确定**
TODO：类似「字符串」的静态方法（减少对象开销）
"""
class NARSPerception(): # 现在不需要枚举类
    
    "内置常量：NARS内置对象名「自我」"
    OBJECT_SELF:str = 'SELF'
    
    @staticmethod
    def new(objective:str, adjective:str):
        "构造感知（与构造函数一致）"
        return NARSPerception(objective, adjective)
    
    @staticmethod
    def new_self(adjective:str):
        "（快捷方式）构造「自身感知」（调用）"
        return NARSPerception(NARSPerception.OBJECT_SELF, adjective)
    
    def __init__(self, objective:str, adjective:str) -> None:
        "构造一个「NARS感知」"
        self.object:str = objective
        self.adjective:str = adjective
    
    def __eq__(self, other) -> bool:
        "相等⇔名称相等"
        return (
            self.object == other.objective
            and self.adjective == other.adjective
        )
    
    def __repr__(self) -> str:
        return "<NARS Perception: {%s} --> [%s] >" % (self.object, self.adjective)
    
    def __str__(self) -> str:
        "字符串就是其「语句」（一般NAL语法）"
        return "<{%s} --> [%s]>." % (self.object, self.adjective)

"""抽象出一个「NARS感知器」
主要功能：作为NARS感知的处理器，根据环境提供的参数生成相应「NARS感知」
- 主要函数：sense(参数) -> 操作集合
TODO：抽象成一个「_perceiveHook: enabled」的字典？
"""
class NARSSensor():
    
    def __init__(self, perceiveHook) -> None:
        self.enabled:bool = True
        self._perceiveHook = perceiveHook
    
    def sense(self,*sense_args:tuple, **sense_targets:dict) -> list[NARSPerception] | tuple[NARSPerception]:
        "感知器的通用调用接口（一定返回感知信息，enabled仅用于NARSAgent的调用之中）"
        return self._perceiveHook(*sense_args, **sense_targets) # 支持外部函数
    
    def __call__(self,*sense_args:tuple, **sense_targets:dict) -> list[NARSPerception] | tuple[NARSPerception]:
        "（语法糖）重载「被调用」语法，快速获取操作"
        return self.sense(*sense_args, **sense_targets)
    
    @property
    def perceiveHook(self):
        return self.perceiveHook
    
    @perceiveHook.setter
    def perceiveHook(self, value):
        "日后可以作为一个「统一更改外界函数」的setter"
        self._perceiveHook = value
