协议结构介绍
============

协议栈结构
----------

.. raw:: html

   <figure class="protocol-stack" aria-labelledby="protocol-stack-caption">
     <div class="protocol-stack__topline">
       <div>
         <span class="protocol-stack__kicker">END-TO-END PROTOCOL MAP</span>
         <span class="protocol-stack__caption" id="protocol-stack-caption">命令从应用语义映射到可插拔传输承载</span>
       </div>
       <div class="protocol-stack__endpoints" aria-label="手机与设备双向通信">
         <span>PHONE</span>
         <i aria-hidden="true"></i>
         <span>DEVICE</span>
       </div>
     </div>
     <div class="protocol-stack__layers">
       <article class="protocol-layer protocol-layer--l2">
         <span class="protocol-layer__id">L2</span>
         <div class="protocol-layer__identity">
           <span class="protocol-layer__name">Application Layer</span>
           <span class="protocol-layer__cn">应用语义层</span>
         </div>
         <div class="protocol-layer__tokens" aria-label="关键协议字段">
           <span>Command</span><span>Length</span><span>Value</span>
         </div>
         <span class="protocol-layer__role">SEMANTIC</span>
       </article>
       <article class="protocol-layer protocol-layer--l1">
         <span class="protocol-layer__id">L1</span>
         <div class="protocol-layer__identity">
           <span class="protocol-layer__name">Transport Layer</span>
           <span class="protocol-layer__cn">可靠传输层</span>
         </div>
         <div class="protocol-layer__tokens" aria-label="关键协议字段">
           <span>Sequence</span><span>ACK</span><span>CRC16</span>
         </div>
         <span class="protocol-layer__role">RELIABLE</span>
       </article>
       <article class="protocol-layer protocol-layer--l0 protocol-layer--adapters">
         <span class="protocol-layer__id">L0</span>
         <div class="protocol-layer__identity">
           <span class="protocol-layer__name">Transport Adapters</span>
           <span class="protocol-layer__cn">可插拔承载层</span>
         </div>
         <div class="protocol-adapters" aria-label="支持的传输承载">
           <div class="protocol-adapter protocol-adapter--ble">
             <span class="protocol-adapter__mark">BLE</span>
             <span class="protocol-adapter__name">UART Profile</span>
             <span class="protocol-adapter__meta">GATT · Write / Notify</span>
           </div>
           <div class="protocol-adapter protocol-adapter--uart">
             <span class="protocol-adapter__mark">UART</span>
             <span class="protocol-adapter__name">Serial</span>
             <span class="protocol-adapter__meta">Bits · Byte stream</span>
           </div>
           <div class="protocol-adapter protocol-adapter--socket">
             <span class="protocol-adapter__mark">SOCKET</span>
             <span class="protocol-adapter__name">Network</span>
             <span class="protocol-adapter__meta">TCP · Stream</span>
           </div>
         </div>
         <span class="protocol-layer__role">PLUGGABLE</span>
       </article>
     </div>
     <div class="protocol-stack__flow" aria-hidden="true">
       <span>APPLICATION DATA</span><i></i><span>RELIABLE FRAME</span><i></i><span>BLE · UART · SOCKET</span>
     </div>
   </figure>

.. note::

   L0 是可插拔接入层，L1/L2 不依赖具体承载。BLE 使用 UART Profile；UART 与 Socket 可复用相同的 L1
   传输语义。当前规范细节以 BLE UART Profile 为主。

.. _l0-uart-profile-ble:

L0 接入承载
-----------

BLE UART Profile
~~~~~~~~~~~~~~~~

.. table:: GATT 服务 UUID
   :class: protocol-table columns-2

   +----------------------+-----------------------------------------------------------------+
   | 角色                 | UUID                                                            |
   +======================+=================================================================+
   | UART Profile Service | ``6e400001-b5a3-f393-e0a9-e50e24dcca9e``                        |
   +----------------------+-----------------------------------------------------------------+
   | Write Characteristic | ``6e400002-b5a3-f393-e0a9-e50e24dcca9e``                        |
   +----------------------+-----------------------------------------------------------------+
   | Read Characteristic  | ``6e400003-b5a3-f393-e0a9-e50e24dcca9e``\ （Notification 模式） |
   +----------------------+-----------------------------------------------------------------+

说明
~~~~

-  **Device 端（Master）**\ ：实现 UART Profile，提供 write + read 两个 characteristic
-  **Phone 端（Slave）**\ ：基于 character operation 实现 write interface 和 receive interface
-  Phone 端 receive 基于 **notify** 模式；Device 端 receive 基于 **write character**\ （push 方式，非 pull）

.. _l1-transport-layer:

L1 传输层
---------

功能
~~~~

-  在 L0 之上实现可靠传输（发送 + 接收）
-  L1 通过拆包/组包支持最大 **65535 bytes** payload（16-bit 长度字段）
-  实现 **ACK 机制**\ ：接收方校验后发送 success/error ACK
-  重传：收到 error ACK 或超时后重发，失败结果上报 L2
-  L1 数据包格式与具体承载解耦，可在 BLE UART Profile、UART、Socket 等链路上复用

L1 数据包结构
~~~~~~~~~~~~~

.. list-table:: L1 Packet（8 ~ 65543 bytes）
   :widths: 30 70
   :class: packet-table

   * - L1 Header（8 bytes）
     - L1 Payload（0 ~ 65535 bytes）

.. table:: L1 Header（8 bytes，Big-Endian）

   +---------+----------------+---------+-------------------------------------------------------------+
   | Byte    | 位域           | 宽度    | 说明                                                        |
   +=========+================+=========+=============================================================+
   | 0       | Magic          | 8 bits  | 固定值 ``0xAB``                                             |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 1 [7:6] | Reserve        | 2 bits  | 保留                                                        |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 1 [5]   | ERR flag       | 1 bit   | 1 = 传输出错                                                |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 1 [4]   | ACK flag       | 1 bit   | 1 = 这是 ACK 包                                             |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 1 [3:0] | Version        | 4 bits  | 当前版本 = 0                                                |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 2~3     | Payload length | 16 bits | Big-Endian，高字节在前                                      |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 4~5     | CRC16          | 16 bits | **CRC-16/ARC**\ ，仅覆盖 Payload（不含 Header），Big-Endian |
   +---------+----------------+---------+-------------------------------------------------------------+
   | 6~7     | Sequence ID    | 16 bits | 包序号，Big-Endian                                          |
   +---------+----------------+---------+-------------------------------------------------------------+

.. table:: ACK 包格式

   =========== =============== =============== =================
   包类型      ACK flag (bit4) ERR flag (bit5) Payload length
   =========== =============== =============== =================
   数据包      0               0               实际 payload 长度
   Success ACK 1               0               0
   Error ACK   1               1               0
   =========== =============== =============== =================

.. note::

   ACK 包的 Sequence ID = 被 ACK 的数据包 Sequence ID。

L1 版本号：\ **0**

.. _l2-application-layer:

L2 应用层
---------

L2 数据包结构
~~~~~~~~~~~~~

.. list-table:: L2 Packet（2 ~ 65535 bytes）
   :widths: 20 80
   :class: packet-table

   * - L2 Header（2 bytes）
     - L2 Payload（0 ~ 65533 bytes）

.. note::

   L2 Payload 上限受 L1 payload 容量约束（最大 65535 B），实际可用大小取决于设备固件缓冲区。

.. list-table:: L2 Header（16 bits，Big-Endian）
   :header-rows: 1
   :widths: 22 16 62
   :class: packet-table bitfield-table

   * - 位域
     - 宽度
     - 说明
   * - Command ID
     - 8 bits
     - 命令类型，见 Command 列表
   * - Version
     - 4 bits
     - L2 版本号
   * - Reserve
     - 4 bits
     - 保留

L2 Payload 结构
~~~~~~~~~~~~~~~

L2 Payload 由连续的 Key-Value 单元组成：Key-Value 1 + Key-Value 2 + …。每个单元的字段顺序如下。

.. list-table:: L2 Payload 单元结构
   :header-rows: 1
   :widths: 38 62
   :class: packet-table payload-unit-table

   * - 字段
     - 长度
   * - Key
     - 1 byte
   * - Key Header
     - 2 bytes
   * - Key Value
     - N bytes

.. list-table:: Key Header（16 bits）
   :header-rows: 1
   :widths: 22 16 62
   :class: packet-table bitfield-table

   * - 位域
     - 宽度
     - 说明
   * - Length
     - 16 bits
     - 该 key 的 value 字节数，最大 65535

.. note::

   Key Header 的 16 bits 全部用于 Length，支持大块传输。
