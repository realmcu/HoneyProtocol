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

* 每个 Key 对应一条测试命令，请求与返回使用成对 Key。
* 多字节整数与时间戳均使用 Big-Endian；时间戳为 4 bytes 墙上时钟秒。
* SN 与测试模式 token 固定 32 bytes，test flag 固定 1 byte。
* Sensor 返回 X / Y / Z 三个有符号 16-bit 值；按键事件固定 8 bytes。

具体命令
--------

.. list-table:: 协议数据示例
   :header-rows: 1
   :widths: 5 12 14 10 15 44
   :class: protocol-table command-detail columns-6

   * - Key
     - 名称
     - 用途
     - 方向
     - 具体的命令
     - 数据说明
   * - 0x01 / 0x02
     - Echo
     - 原样回显
     - 双向
     - ``06 00 01 00 02 4F 4B``；``06 00 02 00 02 4F 4B``
     - 请求与返回 Value 均为 N bytes 字符串
   * - 0x03 / 0x04
     - Charge 信息
     - 查询充电电压
     - 双向
     - ``06 00 03 00 00``；``06 00 04 00 02 0B B8``
     - 返回 Voltage 16 bits，负数表示未检测到
   * - 0x05 / 0x06
     - LED / 马达
     - 点灯或震动
     - 手机 → 设备
     - ``06 00 05 00 01 00``；``06 00 06 00 00``
     - LED 空值表示点亮全部；马达 Value 为空
   * - 0x07 / 0x08 / 0x09
     - SN 写 / 读 / 返回
     - 读写设备序列号
     - 双向
     - ``06 00 07 00 20 30 31 … 66``；``06 00 08 00 00``；``06 00 09 00 20 30 31 … 66``
     - SN 固定 32 bytes
   * - 0x0A / 0x0B / 0x0C
     - test flag
     - 写 / 读 / 返回
     - 双向
     - ``06 00 0A 00 01 01``；``06 00 0B 00 00``；``06 00 0C 00 01 01``
     - Flag 固定 1 byte
   * - 0x0D / 0x0E
     - Sensor 数据
     - 查询三轴数据
     - 双向
     - ``06 00 0D 00 00``；``06 00 0E 00 06 00 64 FF 9C 00 32``
     - X / Y / Z 各 16 bits，Big-Endian
   * - 0x10 / 0x11
     - 测试模式
     - 进入 / 退出
     - 手机 → 设备
     - ``06 00 10 00 20 30 31 … 66``；``06 00 11 00 20 30 31 … 66``
     - 32 bytes token，设备验证后执行
   * - 0x21
     - 按键测试
     - 上报按键事件
     - 设备 → 手机
     - ``06 00 21 00 08 01 06 00 00 6A CC 9A 88``
     - Code 1B + Id 1B + Reserved 2B + Timestamp 4B
   * - 0x31 / 0x32
     - 老化测试
     - 马达 / LED 开始或结束
     - 手机 → 设备
     - ``06 00 31 00 01 01``；``06 00 32 00 01 01``
     - ``01`` 开始，``02`` 结束
