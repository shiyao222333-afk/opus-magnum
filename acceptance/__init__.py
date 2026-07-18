"""巨作(OpusMagnum) 端到端验收 harness。

本包只负责「操作编排」：拉起三器服务 → 喂输入 → 轮询文件夹/摄入日志 → 复制产物 → 清理测试数据。
不做任何审核判定（判定规则由以后单独流程负责）。

代码归属：巨作项目（OpusMagnum）。
当前已注册流程：bilibili_video（馏析→炼真→熔知）。
未来扩展：在 acceptance/flows/ 下新增流程类并用 @register("名") 登记即可。
"""
__version__ = "0.1.0"
