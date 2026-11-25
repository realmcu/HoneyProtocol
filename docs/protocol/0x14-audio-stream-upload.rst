:tocdepth: 2

0x14 音频上传命令
=================

.. container:: doc-status

   **第一版本**\ 　设备麦克风实时上传 Opus 音频流。

.. _cmd-14-section-1:

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
     - 14 00
     - ``14 00`` = Command 0x14，Version 0
   * - Key
     - 1B
     - —
     - 见 :ref:`规则 <cmd-14-section-2>`
   * - Length
     - 2B
     - —
     - Value 字节数，Big-Endian
   * - Value
     - 可变
     - —
     - 见 :ref:`具体命令 <cmd-14-section-3>`

多字节整数均使用 Big-Endian。Opus 数据为裸包，不包含 Ogg 封装、文件头或额外头部。

.. _cmd-14-section-2:

规则
----

1. RECORD_REQ 是可选请求，不是每次上传会话的必备步骤。设备可以由本地操作或其他业务条件自行开始录音，准备完成后直接发送 ``0x01`` START，随后发送 DATA，结束时发送 ``0x03`` STOP。
2. 手机需要主动触发设备录音时，可发送 ``0x05`` RECORD_REQ，Value 为空（Length = 0）。设备接受后发送 START；手机应以 START 作为会话真正开始的唯一标志，不能只根据 RECORD_REQ 发送成功判断录音已开始。
3. 一条 BLE 连接同一时刻只允许一个音频上传会话。会话已存在时，设备忽略重复的 RECORD_REQ；已有会话继续发送，不重新开始。
4. 设备收到 RECORD_REQ 后无法开始录音时发送 ``0x03`` STOP，``reason = 0x04``\ （请求被拒绝），不得发送 START 或 DATA。设备自行开始失败时也可以发送该 STOP；手机以 STOP 结束本次等待。
5. START 的 Value 携带本次流的实际 Opus 参数。手机收到 START 后应初始化 Opus 解码器；收到非 Opus codec 或无法支持的参数时忽略本次会话。
6. 第一版本固定使用 Opus 16 kHz、单声道、20 ms 帧、16 kbps CBR。后续版本可在 Value 末尾追加参数，现有字段保持不变。
7. ``0x02`` DATA 只允许设备发送。手机忽略手机到设备的 DATA。设备发送 STOP 后不得再发送 DATA。
8. ``0x04`` CANCEL_REQ 由手机发送，Value 为空（Length = 0）。设备收到后尽快停止麦克风采样、Opus 编码和 DATA 发送，并发送 STOP，``reason = 0x01``\ （手机取消）。CANCEL_REQ 不单独返回 L2 响应。
9. RECORD_REQ、START、STOP 和 CANCEL_REQ 应请求 L1 ACK。DATA 为实时媒体数据，不建议请求 L1 ACK，避免重传造成队头阻塞；DATA 仍受 L1 CRC 保护，丢失由序号缺口和 Opus PLC 处理。
10. BLE 断开时设备自动结束会话，不保存“正在上传”状态。重连后设备可以自行开始新会话，也可以等待手机发送 RECORD_REQ；无论哪种方式，手机都以收到的 START 作为新会话起点，DATA 序号和流时间重新从 ``0`` 计数。
11. 建议 ATT MTU 不小于 64，连接间隔不大于 30 ms，并优先使用 2M PHY。设备无法满足实时传输条件时不应发送 START；若是响应 RECORD_REQ，则用 STOP 拒绝。
12. 扩展时只在已有 Value 末尾追加字段。接收方忽略未知尾部字段；不得改变已有字段顺序、宽度或含义。

.. list-table:: Key 定义
   :header-rows: 1
   :widths: 12 20 18 50

   * - Key
     - 名称
     - 方向
     - 用途
   * - ``0x01``
     - START
     - 设备 → 手机
     - 设备告知手机：音频上传会话开始，并携带编码参数
   * - ``0x02``
     - DATA
     - 设备 → 手机
     - 一个或多个 Opus 帧，带序号和时间戳
   * - ``0x03``
     - STOP
     - 设备 → 手机
     - 设备告知手机：音频上传会话结束及结束原因
   * - ``0x04``
     - CANCEL_REQ
     - 手机 → 设备
     - 手机要求设备停止当前上传
   * - ``0x05``
     - RECORD_REQ
     - 手机 → 设备
     - 可选：手机主动请求设备开始麦克风录音和音频上传

.. list-table:: START 数据字段
   :header-rows: 1
   :widths: 22 12 66

   * - 字段
     - 大小
     - 说明
   * - codec
     - 1 byte
     - ``0x01`` = Opus
   * - sample_rate
     - 4 bytes
     - 采样率，单位 Hz；第一版本为 ``16000``\ （``00003E80``）
   * - channels
     - 1 byte
     - 声道数；第一版本为 ``1``
   * - frame_ms
     - 1 byte
     - 每帧时长，单位 ms；第一版本为 ``20``\ （``0x14``）
   * - bitrate_bps
     - 2 bytes
     - 编码码率，单位 bit/s；第一版本为 ``16000``\ （``3E80``）
   * - frames_per_packet
     - 1 byte
     - 每个 DATA 建议封装的帧数；第一版本为 ``4``

.. list-table:: STOP reason
   :header-rows: 1
   :widths: 14 28 58

   * - 取值
     - 名称
     - 说明
   * - ``0x00``
     - COMPLETED
     - 设备正常结束上传
   * - ``0x01``
     - CANCELLED_BY_PHONE
     - 设备收到 CANCEL_REQ 后停止
   * - ``0x02``
     - AUDIO_ERROR
     - 麦克风、编码器或音频轨异常导致停止
   * - ``0x03``
     - TRANSPORT_ERROR
     - 设备侧传输资源异常导致停止
   * - ``0x04``
     - REQUEST_REJECTED
     - 设备无法开始录音，拒绝 RECORD_REQ

.. list-table:: STOP 数据字段
   :header-rows: 1
   :widths: 14 12 74

   * - 字段
     - 大小
     - 说明
   * - reason
     - 1 byte
     - 结束原因，见上表

.. list-table:: DATA 数据字段
   :header-rows: 1
   :widths: 20 12 68

   * - 字段
     - 大小
     - 说明
   * - seq
     - 2 bytes
     - DATA 包序号，从 ``0`` 开始递增，回绕到 ``0``；缺口表示丢包
   * - timestamp
     - 4 bytes
     - 包内第一帧的设备流时间，单位 ms；从会话开始计时，允许 32 位回绕
   * - frame_count
     - 1 byte
     - 本包 Opus 帧数，取值 1～4；通常为 4
   * - reserved
     - 1 byte
     - 第一版本必须为 ``0x00``
   * - frames
     - 可变
     - 重复 frame_count 次：2B Opus 长度 + N B Opus 裸包

每个 Opus 帧对应 20 ms PCM。包内后续帧时间按前一个帧递增 20 ms，不因 BLE 到达时间变化。手机遇到 seq 缺口时丢弃当前播放队列并按需执行 Opus PLC，不回送重传请求。

.. _cmd-14-section-3:

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
   * - 0x05
     - RECORD_REQ / 手机可选请求录音
     - 手机 → 设备
     - ``14 00 05 00 00``
     - Value 为空。设备成功时回 START，失败时回 STOP（reason=04），不单独返回 RECORD_REQ 响应。设备也可不等待该请求自行发送 START
   * - 0x01
     - START / 开始音频上传
     - 设备 → 手机
     - ``14 00 01 00 0A 01 00 00 3E 80 01 14 3E 80 04``
     - codec=Opus；16 kHz；单声道；20 ms；16 kbps；每包 4 帧
   * - 0x02
     - DATA / 单帧示例
     - 设备 → 手机
     - ``14 00 02 00 0C 00 00 00 00 00 00 01 00 00 04 0A 0B 0C 0D``
     - seq=0；timestamp=0 ms；1 帧；Opus 长度 4B。Opus 内容仅用于展示布局
   * - 0x03
     - STOP / 正常结束
     - 设备 → 手机
     - ``14 00 03 00 01 00``
     - reason=00，正常结束
   * -
     - STOP / 手机取消
     - 设备 → 手机
     - ``14 00 03 00 01 01``
     - reason=01，设备已按 CANCEL_REQ 停止
   * -
     - STOP / 请求被拒绝
     - 设备 → 手机
     - ``14 00 03 00 01 04``
     - reason=04，设备无法开始录音
   * - 0x04
     - CANCEL_REQ / 手机要求停止
     - 手机 → 设备
     - ``14 00 04 00 00``
     - Value 为空。设备停止 DATA 发送并回 STOP，不单独返回 CANCEL_REQ 响应
