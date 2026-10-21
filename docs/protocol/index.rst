3 L2 Command 详解
=================

.. list-table:: Command 列表
   :header-rows: 1
   :widths: auto

   * - Command ID
     - 命令
     - 规范状态
     - 来源
   * - ``0x01``
     - :doc:`固件升级命令 <0x01-firmware-upgrade>`
     - 未标注
     - 手工维护
   * - ``0x02``
     - :doc:`设置命令 <0x02-settings>`
     - 未标注
     - 工作簿
   * - ``0x03``
     - :doc:`绑定命令 <0x03-bind>`
     - 未标注
     - 工作簿
   * - ``0x04``
     - :doc:`通知命令 <0x04-notification>`
     - 讨论中
     - 工作簿
   * - ``0x05``
     - :doc:`数据命令 <0x05-data>`
     - 讨论中
     - 工作簿
   * - ``0x06``
     - :doc:`工厂测试命令 <0x06-factory-test>`
     - 未标注
     - 手工维护
   * - ``0x08``
     - :doc:`Dump Stack 命令 <0x08-dump-stack>`
     - 未标注
     - 手工维护
   * - ``0x09``
     - :doc:`测试 Flash 读取命令 <0x09-flash-read>`
     - 未标注
     - 手工维护
   * - ``0x0A``
     - :doc:`日志命令 <0x0a-log>`
     - 讨论中
     - 工作簿
   * - ``0x0C``
     - :doc:`BLE 连接参数命令 <0x0c-ble-conn-param>`
     - 未标注
     - 手工维护
   * - ``0x0D``
     - :doc:`WiFi 配网命令 <0x0d-wifi-provision>`
     - 未标注
     - 手工维护
   * - ``0x10``
     - :doc:`文件传输命令 <0x10-file-transfer>`
     - 未标注
     - 手工维护
   * - ``0x11``
     - :doc:`点测命令 <0x11-measurement>`
     - 讨论中
     - 工作簿
   * - ``0x12``
     - :doc:`模拟数据命令 <0x12-simulator>`
     - 讨论中
     - 工作簿
   * - ``0x13``
     - :doc:`音频命令 <0x13-audio>`
     - 讨论中
     - 工作簿

.. note::

   ``0x07`` 与 ``0x0B`` 保留不用。``0x0E``\ （视频流）与 ``0x0F``\ （远程控制）已预留，规范待补。

.. warning:: 工作簿引用缺口

   源工作簿提及以下工作表，但当前文件未包含：``交互示例``、``多条数据示例``、``应用类型``、``待确认``、``数据类型``、``生成规则``。相关描述保留原文，不能据此推断缺失的格式。

.. toctree::
   :maxdepth: 1
   :hidden:

   0x01-firmware-upgrade
   0x02-settings
   0x03-bind
   0x04-notification
   0x05-data
   0x06-factory-test
   0x08-dump-stack
   0x09-flash-read
   0x0a-log
   0x0c-ble-conn-param
   0x0d-wifi-provision
   0x10-file-transfer
   0x11-measurement
   0x12-simulator
   0x13-audio
