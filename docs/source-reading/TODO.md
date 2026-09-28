# TODO

- [ ] **第 3 篇：autofp 模式下 TPACKET_V3 与零拷贝怎么配合**
  - 现象：被动 IDS 且没写 `tpacket-v3` 配置项时，默认启用 V3，不区分运行模式(`src/runmode-af-packet.c:325`)。
  - 疑问：V3 的包用 `PacketSetData()` 零拷贝指向块内数据(`AFPParsePacketV3()`，`src/source-af-packet.c:957`)，而块在 `AFPWalkBlock()` 走完后就由 `AFPFlushBlock()` 还给内核(`src/source-af-packet.c:952`、`1019`)。autofp 下包还在 pickup 队列里等处理线程，块却可能已经还回去了，这时数据是否安全？
  - 待办：读清楚这条路径(必要时实测)，把结论补进第 3 篇第 3 节"V2 和 V3"。
