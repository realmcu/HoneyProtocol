设备端实现状态
==============

本页记录当前设备端实现情况；Excel 中的目标协议见\ `协议规范（Excel 同步） <../protocol/index.html>`__\ 。

.. _command-list:

Command 列表
------------

**实现状态**\ 一列反映设备端固件当前实况：\ **已实现**\ =有完整业务逻辑； **桩**\ =handler 已注册但仅打印日志，收到指令不做任何处理、不回响应（L1 层仍会 ACK，手机端若等待 L2 响应会超时）；\ **未实现**\ =未注册 handler。

.. list-table::
   :header-rows: 1
   :widths: 10 35 35 25

   * - Command ID
     - 设备端实现说明
     - Excel 协议规范
     - 实现状态
   * - ``0x01``
     - :doc:`固件升级命令 <0x01-firmware-upgrade>`
     - 未包含
     - 桩
   * - ``0x02``
     - :doc:`设置命令（旧实现） <0x02-settings>`
     - :doc:`设置命令 <../protocol/0x02-settings>`
     - 已实现（仅 ``0x01`` 时间设置）
   * - ``0x03``
     - :doc:`绑定命令 <0x03-bind>`
     - :doc:`绑定命令 <../protocol/0x03-bind>`
     - 已实现（``0x01`` / ``0x05``）
   * - ``0x04``
     - :doc:`提醒命令（旧实现） <0x04-reminder>`
     - :doc:`通知命令 <../protocol/0x04-notification>`
     - 桩；Excel 已重构 Key
   * - ``0x05``
     - :doc:`运动数据命令（旧实现） <0x05-sport-data>`
     - :doc:`数据命令 <../protocol/0x05-data>`
     - 部分实现；Excel 已重构为通用数据同步
   * - ``0x06``
     - :doc:`工厂测试命令 <0x06-factory-test>`
     - 未包含
     - 桩
   * - ``0x07``
     - :doc:`控制命令（旧实现） <0x07-control>`
     - Excel 中已保留不再使用
     - 桩
   * - ``0x08``
     - :doc:`Dump Stack 命令 <0x08-dump-stack>`
     - 未包含
     - 未实现
   * - ``0x09``
     - :doc:`测试 Flash 读取命令 <0x09-flash-read>`
     - 未包含
     - 未实现
   * - ``0x0a``
     - :doc:`日志命令 <0x0a-log>`
     - :doc:`日志命令 <../protocol/0x0a-log>`
     - 桩
   * - ``0x0c``
     - :doc:`BLE 连接参数命令 <0x0c-ble-conn-param>`
     - 未包含
     - 已实现
   * - ``0x0d``
     - :doc:`WiFi 配网命令 <0x0d-wifi-provision>`
     - 未包含
     - 未实现
   * - ``0x10``
     - :doc:`文件传输命令 <0x10-file-transfer>` （原定 ``0x0b``）
     - 未包含
     - 已实现
   * - ``0x11``
     - 暂无实现说明
     - :doc:`点测命令 <../protocol/0x11-measurement>`
     - 待确认
   * - ``0x12``
     - 暂无实现说明
     - :doc:`模拟数据命令 <../protocol/0x12-simulator>`
     - 待确认
   * - ``0x13``
     - 暂无实现说明
     - :doc:`音频命令 <../protocol/0x13-audio>`
     - 待确认

.. note:: 说明

   设备端头文件 ``hmi_l2.h`` 另外预留了两个本文档未定义的命令： ``0x0e`` （视频流 STREAM）与 ``0x0f`` （远程控制 REMOTE）。两者目前只有宏定义，无 handler 实现，规范待补。

.. toctree::
   :maxdepth: 1
   :hidden:

   0x01-firmware-upgrade
   0x02-settings
   0x03-bind
   0x04-reminder
   0x05-sport-data
   0x06-factory-test
   0x07-control
   0x08-dump-stack
   0x09-flash-read
   0x0a-log
   0x0c-ble-conn-param
   0x0d-wifi-provision
   0x10-file-transfer
