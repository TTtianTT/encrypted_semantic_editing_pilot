# T5Gemma时间/空间固定范围案例

助手审阅POSITION_FIXED_REVIEW_CASES中时间与空间的三个正式seed、plus、首个test世界、当前状态0和两个顺序，共12个原子输出。选集不依赖预测成功；不是12个独立内容世界或独立人工总体标签。raw/gold/文件与checkpoint索引保留。其他方向和世界不继承这些文字标签。

时间与空间两个顺序的dev重构均为100%。时间dev原子seed42/43/44在顺序0为0%、3.82%、0%，顺序1均0%；空间顺序0为0%、1.56%、0%，顺序1均0%。各单元最低分均0，均未准入，连续诊断不执行。这与core已准入的latent组合问题分开。

时间首世界time_0120：外部today必须变为yesterday，事件日期2026-11-27、completed状态、book/green/3 copies和2026-11-24的历史原话three days from now必须保持。

- 三seed顺序0均正确更新外部为yesterday，并保持事件日期/事实，但把固定历史原话three days from now改成two days from now。
- 三seed顺序1均正确更新外部为yesterday，但历史原话同样变为two days from now，历史发话日期又被改成2026-11-25。seed43/44还把绝对事件日期改成2026-11-26；seed42保持2026-11-27。
- 这些不是无法解析的未知段落：完整输出有正常语法/目标关系，明确违反历史锚点和原话保持。重构可以成功，原子范围控制仍失败；没有把事件状态自动从计划改为实际发生。

空间首世界space_0120：David依赖自己的朝向，front顺时针应变为left；固定Emma的right及世界west方向必须保持，parcel/black/6 copies也保持。

- 三seed顺序0均把David的目标关系正确变为to my left，却将固定Emma的right改成front。seed43/44还把世界west改为south；seed42保持west。事实和人物标签保持，是明确的非目标观察者/绝对位置范围破坏。
- 顺序1的seed42/43只输出Observer David和in front of me，目标未旋转且非目标关系/客观事实正文丢失；seed44只输出Observer David和behind me，目标错误且其他必要内容缺失。不将丢失的B观点称为独立证实的B方向错误。

同一世界两顺序输入/gold相同语义，文本位置不同。该固定审阅显示位置敏感性和非目标修改，不能把它单独认定为唯一位置捷径机制。全集原子配对成功、两者均对与覆盖数见position_order_pairs；所有P/N/S/M测试输出保留，未按最好seed选取。
