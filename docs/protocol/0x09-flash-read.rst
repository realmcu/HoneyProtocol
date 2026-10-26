:tocdepth: 2

0x09 测试 Flash 读取命令
========================

命令格式
--------

.. list-table:: L2 命令格式
   :header-rows: 1
   :widths: 18 10 18 54
   :class: protocol-table command-format columns-4

   * - 字段
     - 长度
     - 取值
     - 说明
   * - Header
     - 2B
     - 09 00
     - ``09 00`` = Command 0x09，Version 0
   * - Key
     - 1B
     - —
     - 待定义
   * - Length
     - 2B
     - Value 字节数
     - Big-Endian
   * - Value
     - 可变
     - —
     - 待定义

规则
----

本命令尚未实现。

具体命令
--------

本版本暂无协议数据示例。
