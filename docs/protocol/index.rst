协议规范（Excel 同步）
========================================================================================================================

.. note:: 内容来源

   本目录由 :download:`cavo-realtek-watch-protocol.xlsx <../assets/protocol/cavo-realtek-watch-protocol.xlsx>` 自动生成。
   Excel 是当前新协议的事实来源；``docs/commands/`` 保留设备端实现状态和历史差异说明。

工作簿映射
------------------------------------------------------------------------------------------------------------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - :doc:`0x02 设置命令 <0x02-settings>`
     - ``设置模块(CMD 02)``
     - 未标注
   * - :doc:`0x03 绑定命令 <0x03-bind>`
     - ``绑定模块(CMD 03)``
     - 未标注
   * - :doc:`0x04 通知命令 <0x04-notification>`
     - ``通知模块(CMD 04)``
     - 讨论中
   * - :doc:`0x05 数据命令 <0x05-data>`
     - ``数据模块(CMD 05)``
     - 讨论中
   * - :doc:`0x11 点测命令 <0x11-measurement>`
     - ``点测模块(CMD 11)``
     - 讨论中
   * - :doc:`0x12 模拟数据命令 <0x12-simulator>`
     - ``模拟模块(CMD 12)``
     - 讨论中
   * - :doc:`0x13 音频命令 <0x13-audio>`
     - ``音频模块(CMD 13)``
     - 讨论中
   * - :doc:`0x0A 日志命令 <0x0a-log>`
     - ``日志模块(CMD 0A)``
     - 讨论中
   * - :doc:`天气类型 <weather-types>`
     - ``天气类型``
     - 未标注
   * - :doc:`语音编码 <language-codes>`
     - ``语音编码``
     - 未标注

同步与校验
------------------------------------------------------------------------------------------------------------------------

.. code-block:: bash

   python tools/sync_protocol.py
   python tools/sync_protocol.py --check

导入工具会检查完整报文的 ``v-length``、损坏的公式值、工作簿引用缺口，并生成 ``source.json`` 供 CI 校验。

.. toctree::
   :maxdepth: 1
   :hidden:

   0x02-settings
   0x03-bind
   0x04-notification
   0x05-data
   0x11-measurement
   0x12-simulator
   0x13-audio
   0x0a-log
   weather-types
   language-codes
