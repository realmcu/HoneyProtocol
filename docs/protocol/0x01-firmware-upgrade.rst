:tocdepth: 2

0x01 固件升级命令
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
     - 01 00
     - ``01 00`` = Command 0x01，Version 0
   * - Key
     - 1B
     - 见规则
     - 每条消息一个 Key
   * - Length
     - 2B
     - Value 字节数
     - Big-Endian
   * - Value
     - 可变
     - 见具体命令
     - 请求为空，返回 2B

规则
----

* 设备仅在收到 ``0x01`` 请求后进入固件升级模式。
* ``0x02`` 的 Value 固定为 Status 1 byte + Error 1 byte；Error 仅在 Status = ``0x01`` 时有效。

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
   * - 0x01
     - 固件升级请求
     - 进入升级模式
     - 手机 → 设备
     - ``01 00 01 00 00``
     - Value 空（Length = 0）
   * - 0x02
     - 升级返回
     - 升级成功
     - 设备 → 手机
     - ``01 00 02 00 02 00 00``
     - Status = ``00``，Error = ``00``
   * - 0x02
     - 升级返回
     - OTA 失败
     - 设备 → 手机
     - ``01 00 02 00 02 00 01``
     - Status = 01，Error = 01（电量过低）
