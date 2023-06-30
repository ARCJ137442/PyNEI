"""衍生项目：NARS in 井字棋"""

from sys import path as PATH, argv as ARGV
from os import getcwd # 获取当前路径

IS_ROOT_GAME:str = 'game' in getcwd() # 由于VSCode调试路径为项目根目录，故需要识别当前路径
CIN_ROOT_PATH:str = r'..\PyNEI' if IS_ROOT_GAME else r'.\PyNEI' # 调用的CIN路径还要动态决定（Windows cmd使用反斜杠做路径分割）……

PATH.append('../' if IS_ROOT_GAME else './') # 若为直接启动（含game目录），则变为上级路径
# 📌一个「.」或「./」代表项目根目录：用于VSCode调试（默认路径变成项目根目录）
# 📌两个「..」或「./../」代表上层目录：添加上级目录到「环境变量」中，使Python可以跨文件夹访问库

from PyNEI.Agent import NARSAgent, NARSType, NARSOperation, NARSPerception, NARSSensor

from itertools import product

# 设置游戏板和棋子的属性
BOARD_SIZE = 3  # 棋盘大小
marker:list[list[None|str]] = None  # 记录棋盘状态

class NARSPlayer(NARSAgent):
    
    POS_RANGE = range(BOARD_SIZE*BOARD_SIZE)
    "位置0~8 可遍历对象"
    
    POS_TRANSFORM_TUPLE:dict[int:tuple[int,int]] = {
        i: (i//3, i%3)
        for i in POS_RANGE
    }
    "位置0~8⇒坐标(x,y)"
    
    POS_TRANSFORM_INV:dict[tuple[int,int]:int] = {
        v: k
        for k,v in POS_TRANSFORM_TUPLE.items()
    }
    "坐标(x,y) ⇒ 位置0~8"
    
    POS_TRANSFORM_STR:dict[int:str] = {
        k: '%d_%d' % v
        for k,v in POS_TRANSFORM_TUPLE.items()
    }
    "位置0~8 ⇒ 字符串（用于嵌入NAL语句）"
    
    # NAL词项区 #
    
    OPERATION_SET:dict[int:NARSOperation] = {
        k: NARSOperation(f'place_{v}')
        for k,v in POS_TRANSFORM_STR.items()
    }
    "位置0~8 ⇒ NARS操作（根据坐标生成操作）"
    
    # 定义目标
    GOAL_GOOD:str = 'good'
    GOAL_BAD:str = None # 负向目标
    
    # 定义感知名
    
    # 对象：只需要名字，其会被自动转换为「{对象名}」
    OBJECT_BOARD:str = 'board'
    
    "坐标转换：数字0~8⇒词项"
    OBJECT_POINTS:dict = {
        k: f'pos_{v}'
        for k,v in POS_TRANSFORM_STR.items()
    }
    
    # 状态：只需要名字，其会被自动转换为「[状态名]」
    "每个坐标的所有可能状态"
    ADJECTIVE_MARKERS:list[str] = ['X', 'O', None]
    
    # 根据词项生成（静态）感知
    "(坐标0~8, 状态) -> 感知"
    SNESE_POS:dict = {
        (pos, marker): NARSPerception(obj, marker)
        for (pos,obj), marker in product(OBJECT_POINTS.items(), ADJECTIVE_MARKERS)
    }
    
    # 适配ONA #
    ONA_OP_LIST:list[str] = [
        'activate',
        'deactivate',
        'down',
        'drop',
        'go',
        'left',
        'pick',
        'right',
        'say',
        'up',
    ]
    
    def __init__(self, nars_type: NARSType = None):
        super().__init__(
            rootPath = CIN_ROOT_PATH,
            nars_type = nars_type,
            mainGoal = NARSPlayer.GOAL_GOOD,
            mainGoal_negative = NARSPlayer.GOAL_BAD # NARSPlayer.GOAL_BAD
            ) # 目标：「good」
        # 添加感知器
        # self.add_sensor(NARSSensor(NARSPlayer.sensor_board)) # 棋盘感知
        self.add_sensor(NARSSensor(NARSPlayer.sensor_board_aggregate)) # 棋盘感知
        # 注册基本操作
        self.register_basic_operations(*list(NARSPlayer.OPERATION_SET.values()))
    
    # 感知
    def handle_program_operation(self, operation:NARSOperation):
        "操作名的「别名分发」"
        
        if self.type == NARSType.ONA:
            if operation.name in NARSPlayer.ONA_OP_LIST:
                operation = NARSPlayer.OPERATION_SET[
                    NARSPlayer.ONA_OP_LIST.index(operation.name) % 9 # 直接「暴力映射」
                ]
        
        # 打印操作以跟踪
        print(operation.value)
        
        # 添加操作
        super().handle_program_operation(operation)
    
    @staticmethod
    def sensor_board(*sense_args:tuple, **sense_targets:dict) -> list[NARSPerception]:
        marker:list[list[None|str]] = sense_args[0] # 获取棋盘
        result:list[NARSPerception] = []
        
        for i in range(len(marker)):
            for j in range(len(marker[i])): # 遍历棋盘所有方格
                result.append(
                    NARSPlayer.SNESE_POS[
                        NARSPlayer.POS_TRANSFORM_INV[i,j],
                        marker[i][j]
                    ]
                )
        
        return result
    
    @staticmethod
    def sensor_board_aggregate(*sense_args:tuple, **sense_targets:dict) -> list[NARSPerception]:
        marker:list[list[None|str]] = sense_args[0] # 获取棋盘
        result:list[NARSPerception] = []
        global markers_str # 调用全局的函数
        
        return [NARSPerception(
            NARSPlayer.OBJECT_BOARD,
            markers_str(marker, '', '', '_')
        )]

#---- Origin Author: ChatGPT ---#

import pygame
import sys

from random import randint
def agent_random(playerName):
    pos = randint(0,8)
    if place(
        x := pos // 3,
        y := pos % 3,
        playerName
    ):
        print(f'放置({x},{y}) by {playerName}({players[playerName]})')

def agent_spare(playerName):
    for pos in range(BOARD_SIZE*BOARD_SIZE):
        if place(
            x := pos // 3,
            y := pos % 3,
            playerName
        ):
            print(f'放置({x},{y}) by {playerName}({players[playerName]})')
            break

AGENT_FUNC:dict = {
    'random': agent_random,
    'spare': agent_spare,
}

def getPlayer(prompt:str) -> NARSPlayer|str:
    "获取一个NARS玩家（兼容特殊模式）"
    global AGENT_FUNC
    type_str:str = input(prompt)
    try:
        t = NARSType(type_str) if type_str else NARSType.PYTHON
        return NARSPlayer(t)
    except:
        t = type_str if type_str else None # 兼容特殊代码
    if t in AGENT_FUNC:
        print(f'Selected special type {t}!')
    else:
        print('Exception passed.')
    return t

"所有玩家类型"
players:dict[str, NARSPlayer|str] = {
    'X': None,
    'O': None,
}

def installNARSes(narses):
    "添加NARS"
    for key in narses:
        if not narses[key]: # 若无则填充
            narses[key] = getPlayer(f'type of player {key}: ')

installNARSes(players)

# 绘制棋盘

def markers_str(markers, rowsep:str='\n', colsep:str='', empty:str='_'):
    return rowsep.join(
        colsep.join(
            markers[i][j][0:1] # 截取第一个字符
            if markers[i][j] # 防None
            else empty
            for j in range(BOARD_SIZE)
        )
        for i in range(BOARD_SIZE)
    )

def print_markers():
    global marker
    print(markers_str(markers=marker))

def draw_board() -> bool:
    '绘制棋盘'
    print_markers()
    
    if not pygame.get_init():
        return False
    SCREEN.fill(WHITE)

    # 绘制水平和垂直线条
    for i in range(1, BOARD_SIZE):
        pygame.draw.line(SCREEN, BLACK, (0, i * CELL_SIZE), (WIDTH, i * CELL_SIZE))
        pygame.draw.line(SCREEN, BLACK, (i * CELL_SIZE, 0), (i * CELL_SIZE, HEIGHT))

    # 绘制棋子
    for i in range(len(marker)):
        for j in range(len(marker[i])):
            if marker[i][j] == "X":
                draw_x(i, j)
            elif marker[i][j] == "O":
                draw_o(i, j)
    
    return True

# 绘制X形的棋子
def draw_x(row, col):
    x = col * CELL_SIZE
    y = row * CELL_SIZE
    pygame.draw.line(SCREEN, BLACK, (x, y), (x + CELL_SIZE, y + CELL_SIZE), 2)
    pygame.draw.line(SCREEN, BLACK, (x, y + CELL_SIZE), (x + CELL_SIZE, y), 2)

# 绘制O形的棋子
def draw_o(row, col):
    centerX = int(col * CELL_SIZE + CELL_SIZE // 2)
    centerY = int(row * CELL_SIZE + CELL_SIZE // 2)
    radius = int(CELL_SIZE // 2 - 5)
    pygame.draw.circle(SCREEN, BLACK, (centerX, centerY), radius, 2)

# 检查游戏是否结束
def is_game_over():
    # 水平和垂直方向
    for i in range(BOARD_SIZE):
        if marker[i][0] == marker[i][1] == marker[i][2] != None:
            return marker[i][0]
        if marker[0][i] == marker[1][i] == marker[2][i] != None:
            return marker[0][i]
    
    # 对角线方向
    if marker[0][0] == marker[1][1] == marker[2][2] != None:
        return marker[0][0]
    if marker[0][2] == marker[1][1] == marker[2][0] != None:
        return marker[0][2]
    
    # 检查非空
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if marker[i][j] == None:
                return None
    
    return ' '

# 计时器
UPDATE_PLAYER_EVENT = pygame.USEREVENT
UPDATE_NARS_EVENT_TIMER = int(i if (i:=input('Input UPDATE_NARS_EVENT_TIMER: ')) else 200)
timer_update_NARS = int(UPDATE_NARS_EVENT_TIMER)

def set_timers():
    pygame.time.set_timer(UPDATE_PLAYER_EVENT, timer_update_NARS)  # the activity of NARS

def reset_game():
    global marker, current_player
    marker = [[None] * BOARD_SIZE for _ in range(BOARD_SIZE)]
    current_player = "X"
    draw_board()

stat_win:dict[str:int] = {}

def game_win(winner):
    global stat_win, players
    if winner == ' ':
            print('No player win!')
            winner = None
    else:
        print(f'Player "{winner}" win!')
    # 更新数据
    stat_win[winner] = stat_win.get(winner,0) + 1
    print(stat_win)
    # 更新NARS
    for mark, nars in players.items():
        isinstance(nars, NARSPlayer) and (
            nars.praise_goal
            if mark == winner
            else nars.punish_goal
        )(nars.GOAL_GOOD)

# 放置
def place(row, col, player) -> bool:
    "尝试放置棋子，并返回「是否放置成功」"
    global marker, current_player, TIME_FOR_WAIT
    
    # 更新棋盘
    if marker[row][col] == None:
        marker[row][col] = player
        
        print(f'落子[{row},{col}] = {player}')
        
        # 轮换玩家 TODO: 外置出去
        if player == "X":
            current_player = "O"
        else:
            current_player = "X"
        
        # 刷新画板
        draw_board()

        # 检测胜利
        if winner:=is_game_over():
            game_win(winner)
            # 重置游戏
            TIME_FOR_WAIT>0 and pygame.time.wait(TIME_FOR_WAIT) # 等待
            reset_game()
            
        # 更新所有NARS的感知
        for player,nars in players.items():
            isinstance(nars, NARSPlayer) and nars.update(marker)
        return True
    return False

max_babble_time:int = int(i if (i:=input('Input max_babble_time: ')) else 20)

babble_time:int = 0

def delete_nars(player:str):
    global players
    nars = players[player]
    if nars:
        nars.disconnect_brain()
        players[player] = None

def clearStat(stat:dict[str:int]) -> dict:
    for player in stat:
        stat[player] = 0
    return stat

def pretrain(count:int):
    '预训练：两个AI相互博弈，最后保留分数高的那一个'
    global stat_win, TIME_FOR_WAIT
    
    TIME_FOR_WAIT *= -1
    
    clearStat(stat_win)
    # 训练
    while sum(stat_win.values()) < count: # 游戏总局数
        update_players()
    print(f'Pretrain completed:', stat_win)
    # 取胜利数量最大的一个AI
    winner, max_win = max(stat_win.items(), key=lambda x:x[1]) # 取value（胜利数）
    for player, nars in players.items():
        if player == winner:
            continue
        # 清除
        playerType = players[player].type.value if (isNARS:=isinstance(nars, NARSPlayer)) else players[player]
        print(f'Deleted player {player}({playerType}) with n_win={stat_win[player]}')
        if isNARS:
            delete_nars(player)
        else:
            players[player] = None
    print(f'Picked player {winner}({players[winner]}) with n_win={max_win}')
    # 清除胜利统计
    clearStat(stat_win)
    
    TIME_FOR_WAIT *= -1

def handle_operation(nars:NARSPlayer, player:str) -> bool:
    "处理NARS的操作 输出：是否有处理操作"
    global players, current_player, babble_time, max_babble_time
    aonl = list(nars.active_operation_names)
    for operation_name in aonl: # 使用list防止运行时改变
        if len(ons:=operation_name.split('_')) == 3: # 防止参数不够
            _,x,y = ons
            x,y = int(x), int(y)
            if place(x,y,player):
                print(f'放置({x},{y}) by {player}({nars.type.value})')
                babble_time = max_babble_time # 重置babble计时器
                nars.praise_goal('valid') # 成功
            else:
                # 放置失败：惩罚
                nars.punish_goal('valid')
                nars.put_goal('valid')
            # 执行一次就清空
            nars.reset_stored_operations()
            return True # 防止按多次
        else:
            print(f'error: {operation_name}')
    else:
        return False
    return False

def update_players():
    global players, current_player, babble_time, max_babble_time, AGENT_FUNC
    if isinstance(player:=players[current_player], NARSPlayer):
        # 劫持NARS操作
        if not handle_operation(player, current_player):
            if babble_time > 0:
                print('.', end='')
                babble_time -= 1
            elif babble_time == 0:
                # 若无操作,babble(惩罚)
                print(f'babble({current_player}@{player.type.value})')
                player.babble(1, NARSPlayer.OPERATION_SET)
                babble_time = max_babble_time
                
                player.punish_goal('valid')
                player.put_goal('valid')
    elif agentFunc:=AGENT_FUNC.get(player, None) :
        agentFunc(current_player)
    
TIME_FOR_WAIT:int = 2000 # 每次游戏结束后，延迟重置游戏的时间

# 主循环
if __name__ == '__main__':
    
    reset_game()
    
    if pretrain_num:=input('Steps to pretrain: '):
        pretrain(int(pretrain_num))

    # 初始化游戏
    pygame.init()

    # 设置窗口大小和标题
    WIDTH, HEIGHT = 300, 300
    CELL_SIZE = WIDTH // BOARD_SIZE  # 单元格大小
    WINDOW_SIZE = (WIDTH, HEIGHT)
    SCREEN = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("井字棋")

    # 设置颜色
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    
    set_timers()
    
    while True:
        for event in pygame.event.get():
            
            # 游戏退出
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            # 更新NARS操作
            elif event.type == UPDATE_PLAYER_EVENT:
                update_players()
                    
            # 鼠标按键
            elif event.type == pygame.MOUSEBUTTONDOWN and not is_game_over():
                mouseX, mouseY = pygame.mouse.get_pos()
                clicked_row = mouseY // CELL_SIZE
                clicked_col = mouseX // CELL_SIZE
                place(clicked_row,clicked_col,current_player)
            
            # 数据追踪
            elif event.type == pygame.KEYDOWN:
                key = event.key
                if key == pygame.K_p:
                    "预训练"
                    installNARSes(players) # 重新装载AI
                    # 预训练
                    if pretrain_num:=input('Steps to pretrain: '):
                        pretrain(int(pretrain_num))
                if key == pygame.K_d:
                    "预训练"
                    delete_nars(input('Choose what player will be deleted: '))
                else:
                    babble_time *= -1
                    print(f'enable_babble = {babble_time >= 0}')

        pygame.display.update()