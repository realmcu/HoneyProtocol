# 3.7 工厂测试命令 (command id 0x06)

L2 版本号：**0**

| Key    | 定义                     |
|--------|--------------------------|
| `0x01` | 请求 echo 服务           |
| `0x02` | Echo 服务返回            |
| `0x03` | 请求 charge 信息         |
| `0x04` | 返回 charge 信息         |
| `0x05` | 点亮 LED                 |
| `0x06` | 震动马达                 |
| `0x07` | 写 SN                    |
| `0x08` | 读 SN                    |
| `0x09` | SN 返回                  |
| `0x0a` | 写 test flag             |
| `0x0b` | 读 test flag             |
| `0x0c` | test flag 返回           |
| `0x0d` | 请求 sensor 数据         |
| `0x0e` | 返回 sensor 数据         |
| `0x10` | 进入测试模式（超级命令） |
| `0x11` | 退出测试模式（超级命令） |
| `0x21` | 按键测试                 |
| `0x31` | 马达老化测试             |
| `0x32` | LED 老化测试             |

## 0x01/0x02 — Echo

请求 Value：N bytes 字符串；返回 Value：原封不动返回

## 0x03/0x04 — Charge 信息

请求 Value：空；返回 **Value（2 bytes）**：Voltage（16 bits，负数表示未检测到）

## 0x05 — 点亮 LED

**Value**：空=点亮所有 LED；`0x00`=第一行；`0x01`=第二行；...

## 0x06 — 震动马达

**Value**：空

## 0x07/0x08/0x09 — SN 写/读/返回

写请求/返回 Value：32 bytes SN；读请求 Value：空

## 0x0a/0x0b/0x0c — test flag 写/读/返回

写请求/返回 Value：1 byte flag；读请求 Value：空

## 0x0d/0x0e — sensor 数据请求/返回

请求 Value：空；返回 **Value（48 bits）**：X axis（16b）+ Y axis（16b）+ Z axis（16b）

## 0x10/0x11 — 进入/退出测试模式

**Value**：32 bytes token（设备验证通过后才执行）

## 0x21 — 按键测试

**方向**：设备 → 手机 \| **Value（8 bytes）**：

| 字段      | 大小    | 说明                                                          |
|-----------|---------|---------------------------------------------------------------|
| Code      | 1 byte  | `0x00`=DOWN；`0x01`=UP；`0x02`=SHORT_CLICK；`0x03`=LONG_CLICK |
| Id        | 1 byte  | Button ID                                                     |
| Reserved  | 2 bytes | —                                                             |
| Timestamp | 4 bytes | 墙上时钟秒（自 1970-01-01 起算，与 §0x01 定义一致）           |

## 0x31/0x32 — 马达/LED 老化测试

**Value（1 byte）**：`0x01`=开始；`0x02`=结束
