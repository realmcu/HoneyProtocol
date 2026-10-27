:tocdepth: 2

0x06 工厂测试命令
=================

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
     - 06 00
     - ``06 00`` = Command 0x06，Version 0
   * - Key
     - 1B
     - 见规则
     - 每条测试命令一个 Key
   * - Length
     - 2B
     - Value 字节数
     - Big-Endian
   * - Value
     - 可变
     - 见具体命令
     - 各测试命令独立定义

规则
----

1. 每个 Key 对应一条测试命令，请求与返回使用成对 Key。
2. 多字节整数与时间戳均使用 Big-Endian；时间戳为 4 bytes 墙上时钟秒。
3. SN 与测试模式 token 固定 32 bytes，test flag 固定 1 byte。
4. Sensor 返回 X / Y / Z 三个有符号 16-bit 值；按键事件固定 8 bytes。

具体命令
--------

.. list-table:: 协议数据示例
   :header-rows: 1
   :widths: 5 20 10 15 50
   :class: protocol-table command-detail columns-5

   * - Key
     - 名称 / 用途
     - 方向
     - 具体的命令
     - 数据说明
   * - 0x01
     - Echo 请求 / 原样回显
     - 手机 → 设备
     - ``06 00 01 00 02 4F 4B``
     - 请求 Value 为 N bytes 字符串
   * - 0x02
     - Echo 返回 / 原样回显
     - 设备 → 手机
     - ``06 00 02 00 02 4F 4B``
     - 返回 Value 为 N bytes 字符串
   * - 0x03
     - Charge 信息请求 / 查询充电电压
     - 手机 → 设备
     - ``06 00 03 00 00``
     - Value 空（Length = 0）
   * - 0x04
     - Charge 信息返回 / 电压值
     - 设备 → 手机
     - ``06 00 04 00 02 0B B8``
     - Voltage 16 bits，负数表示未检测到
   * - 0x05
     - LED 点亮 / 选择 LED 行
     - 手机 → 设备
     - ``06 00 05 00 01 00``
     - Value 1B：空表示全部，``00``、``01``… 分别表示第一行、第二行…
   * - 0x06
     - 马达震动 / 启动震动
     - 手机 → 设备
     - ``06 00 06 00 00``
     - Value 空（Length = 0）
   * - 0x07
     - SN 写入 / 写设备序列号
     - 手机 → 设备
     - ``06 00 07 00 20 30 31 … 66``
     - SN 固定 32 bytes
   * - 0x08
     - SN 读取 / 读取请求
     - 手机 → 设备
     - ``06 00 08 00 00``
     - Value 空（Length = 0）
   * - 0x09
     - SN 返回 / 当前序列号
     - 设备 → 手机
     - ``06 00 09 00 20 30 31 … 66``
     - SN 固定 32 bytes
   * - 0x0A
     - test flag 写入 / 设置标志
     - 手机 → 设备
     - ``06 00 0A 00 01 01``
     - Flag 固定 1 byte
   * - 0x0B
     - test flag 读取 / 读取请求
     - 手机 → 设备
     - ``06 00 0B 00 00``
     - Value 空（Length = 0）
   * - 0x0C
     - test flag 返回 / 当前标志
     - 设备 → 手机
     - ``06 00 0C 00 01 01``
     - Flag 固定 1 byte
   * - 0x0D
     - Sensor 数据请求 / 三轴查询
     - 手机 → 设备
     - ``06 00 0D 00 00``
     - Value 空（Length = 0）
   * - 0x0E
     - Sensor 数据返回 / 三轴数据
     - 设备 → 手机
     - ``06 00 0E 00 06 00 64 FF 9C 00 32``
     - X / Y / Z 各 16 bits，Big-Endian
   * - 0x10
     - 进入测试模式 / 超级命令
     - 手机 → 设备
     - ``06 00 10 00 20 30 31 … 66``
     - 32 bytes token，设备验证后执行
   * - 0x11
     - 退出测试模式 / 超级命令
     - 手机 → 设备
     - ``06 00 11 00 20 30 31 … 66``
     - 32 bytes token，设备验证后执行
   * - 0x21
     - 按键测试 / 上报按键事件
     - 设备 → 手机
     - ``06 00 21 00 08 01 06 00 00 6A CC 9A 88``
     - Code 1B + Id 1B + Reserved 2B + Timestamp 4B
   * - 0x31
     - 马达老化测试 / 启停控制
     - 手机 → 设备
     - ``06 00 31 00 01 01``
     - ``01`` 开始，``02`` 结束
   * - 0x32
     - LED 老化测试 / 启停控制
     - 手机 → 设备
     - ``06 00 32 00 01 01``
     - ``01`` 开始，``02`` 结束
