:tocdepth: 2

0x08 Dump Stack 命令
====================

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
     - 08 00
     - ``08 00`` = Command 0x08，Version 0
   * - Key
     - 1B
     - 见规则
     - 请求与返回各一个 Key
   * - Length
     - 2B
     - Value 字节数
     - Big-Endian
   * - Value
     - 可变
     - 见具体命令
     - 本版本尚未实现

规则
----

本命令尚未实现。以下 Key 为协议预留定义。

.. table:: 消息定义

   ======== ================================
   Key      定义
   ======== ================================
   ``0x01`` 手机请求获取手环 assert 位置信息
   ``0x02`` 手环返回 assert 位置信息
   ``0x03`` 手机请求获取 assert 栈信息
   ``0x04`` 手环反馈 assert 栈信息
   ======== ================================

具体命令
--------

本版本暂无协议数据示例。
