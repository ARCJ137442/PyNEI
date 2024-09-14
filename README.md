# NARS-Embodied-Interface NARS具身接口

![GitHub License](https://img.shields.io/github/license/ARCJ137442/PyNEI?style=for-the-badge&color=0288d1)
![Code Size](https://img.shields.io/github/languages/code-size/ARCJ137442/PyNEI?style=for-the-badge&color=0288d1)
![Lines of Code](https://www.aschey.tech/tokei/github.com/ARCJ137442/PyNEI?style=for-the-badge&color=0288d1)
[![Language](https://img.shields.io/badge/language-Python-blue?style=for-the-badge&color=0288d1)](https://www.python.org/)

开发状态：

![Created At](https://img.shields.io/github/created-at/ARCJ137442/PyNEI?style=for-the-badge)
![Last Commit](https://img.shields.io/github/last-commit/ARCJ137442/PyNEI?style=for-the-badge)

[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-2.0.0-%23FE5196?style=for-the-badge)](https://conventionalcommits.org)

## 简介

一个以 ***NARS*** 作为AI玩家，提供集成访问&调用的接口

- 前身：
  - **徐博洋「NARS战机」：[Noctis-Xu/NARS-FighterPlane](https://github.com/Noctis-Xu/NARS-FighterPlane)**
  - [ARCJ137442/NARS-FighterPlane](https://github.com/ARCJ137442/NARS-FighterPlane/tree/master/NARS-FighterPlane_v2.i_alpha) v2.i_alpha
- 缩写：NEI

## Concept 概念

- NARS: Non-Axiomatic Reasoning System | 非公理推理系统
- NAL: Non-Axiomatic Logic | 非公理逻辑
- CIN: Computer Implementation of NARS  | NARS的计算机实现

## Preparation 预备

1. Python 3.11+
2. PyGame（若需运行游戏）

## Feature 特性

- 更通用化的具身接口代码
  - 将「智能体定义」和「与NARS程序通信」分离
  - 集中定义NAL语句，避免分散与重复
  - 更高的代码重用率
- 异步CIN进程管理机制
  - 一个子进程启动CIN实例
  - 两个附属子线程，分别负责I/O操作

## References 参考

NARS计算机实现

- OpenNARS: <https://github.com/opennars/opennars>
- ONA: <https://github.com/opennars/OpenNARS-for-Applications>
- NARS-in-Python: <https://github.com/ccrock4t/NARS-Python>

NARS+ & 游戏Demo

- NARS-Pong in Unity3D: <https://github.com/ccrock4t/NARS-Pong>
- NARS-FighterPlane by Boyang Xu: <https://github.com/Noctis-Xu/NARS-FighterPlane>
- ARCJ137442/NARS-FighterPlane: <https://github.com/ARCJ137442/NARS-FighterPlane>
