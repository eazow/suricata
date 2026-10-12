# TODO

- [ ] **第 3 篇：autofp 模式下 TPACKET_V3 与零拷贝怎么配合**
  - 现象：被动 IDS 且没写 `tpacket-v3` 配置项时，默认启用 V3，不区分运行模式(`src/runmode-af-packet.c:325`)。
  - 疑问：V3 的包用 `PacketSetData()` 零拷贝指向块内数据(`AFPParsePacketV3()`，`src/source-af-packet.c:957`)，而块在 `AFPWalkBlock()` 走完后就由 `AFPFlushBlock()` 还给内核(`src/source-af-packet.c:952`、`1019`)。autofp 下包还在 pickup 队列里等处理线程，块却可能已经还回去了，这时数据是否安全？
  - 待办：读清楚这条路径(必要时实测)，把结论补进第 3 篇第 3 节"V2 和 V3"。

- [ ] **番外：Suricata 里的红黑树**
  - 缘起：第 6 篇的 TCP 段放在红黑树 `seg_tree` 里，但没展开讲红黑树本身。
  - 实现：`src/tree.h`，来自 BSD(NetBSD/OpenBSD/FreeBSD，Niels Provos)的宏实现。`RB_HEAD`、`RB_ENTRY`、`RB_GENERATE` 这类宏按类型生成代码，节点指针直接嵌在业务结构体里(侵入式)，不用额外分配节点。
  - 用到的地方(`RB_HEAD` 声明)：
    - TCP 段 `TCPSEG`(`src/stream-tcp-private.h:91`)、SACK 记录 `TCPSACK`(`src/stream-tcp-private.h:55`)
    - 流式缓冲区的数据块 `SBB`(`src/util-streaming-buffer.h:104`)
    - IP 分片 `IP_FRAGMENTS`(`src/defrag.h:77`)
    - HTTP Range 请求 `HTTP_RANGES`(`src/app-layer-htp-range.h:48`)
    - 端口区间树：`src/interval-tree.h` 在红黑树上扩展出区间树(`IRB_HEAD`)，用于规则的端口分组(`src/detect-engine-port.h:40`)
  - 可以讲的点：红黑树的性质和旋转；为什么这些场景都选红黑树(按序号/偏移有序、频繁插入删除、要查重叠区间)；宏生成代码 vs 泛型；区间树怎么在红黑树上扩展。
