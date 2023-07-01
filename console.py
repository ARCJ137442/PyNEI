
from PyNEI.Program import NARSType # 同路径相对导入使用「.文件名」
from PyNEI.Console import NARSConsole

def main():
    nars_type:NARSType = (
        NARSType(ARGV[1]) if len(ARGV)>1
        else NARSType(type)
        if (type:=input("Please input the type of NARS(opennars(default)/ONA/python): "))
        else NARSType.OPENNARS
    )
    console:NARSConsole = NARSConsole(
        type = nars_type,
        rootPath = CIN_ROOT_PATH,
        asyncOut = True, # 启用异步输出
        inputPrompt = '' # 无prompt（因异步输出会对屏幕文字产生干扰）
    )
    console.launch()
    print()

if __name__ == '__main__':

    from sys import path as PATH, argv as ARGV
    from os import getcwd # 获取当前路径

    IS_ROOT_GAME:str = 'game' in getcwd() # 由于VSCode调试路径为项目根目录，故需要识别当前路径
    CIN_ROOT_PATH:str = '..\PyNEI' if IS_ROOT_GAME else '.\PyNEI' # 调用的CIN路径还要动态决定……
    
    while 1:
        main()