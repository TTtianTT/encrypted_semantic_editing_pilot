# T5Gemma人称固定句序案例及归属评分边界

助手审阅三个seed、首个test世界person_0120、状态0、plus和两个顺序共六个原子输出。选择不依赖成功。目标新语境是Speaker Carol/Listener Henry；主事件保持Grace给Carol、Henry拥有parcel，white和4 copies。历史Carol对Henry说的I give you my key必须保持同一引语语境和原话。原始数据/预测/gold/哈希见POSITION_FIXED_REVIEW_CASES；这些不是六个独立世界。

|seed|目标在前|历史引语在前|
|---|---|---|
|42|Speaker/Listener和主事件/事实正确。I said to Henry在实际Speaker Carol下仍表示历史发话者Carol，且引语内部原话未变；该输出语义正确，原姓名字面比较是保守假阴性。独立actual-header归属复核成功。|Speaker Henry/Listener Carol不是目标语境；输出Carol gives me her key，主parcel事件及客观事实和直接引语缺失。|
|43|新语境和主事件/事实正确；I said to Grace把历史受话者从Henry改成Grace，内部又变成You give me Henry's key，违反历史语境/原话保持。|Speaker Henry/Listener Carol不是目标；输出Carol gives me her key，必要主事件/事实和直接引语缺失。|
|44|新语境和主事件/事实正确；I said to Grace改变历史受话者，内部You give Henry my key改变历史原话及其施事绑定。|Speaker Henry/Listener Carol不是目标；输出she gives me her key，身份无法从完整输出确定，主parcel事件、事实及直接引语缺失。|

不将合法的引语外I当作历史发话者换人。引语内部的I/you不得按外部Speaker/Listener重新绑定；post hoc归属适配器只依据实际输出的唯一Speaker/Listener，在引语外解析I/you主格及me/you宾格，quote words保持。错误实际语境、错误历史受话者、格错误和历史原话修改不会被修复，1,008正例/6,048负例及保护例检查通过。

person_quote_attribution_by_seed对全部person输出统一重评，明确split和evaluation_artifact，dev/test与原子/gold续步不混合。所有原分数、准入、checkpoint和cohort保持。复核不改变core及source matrix（没有历史归属句）。该人称结构仍未达到原子阈值：历史原话大量被改写，且T5Gemma两顺序的原重构dev分数分别55.56%与34.72%；修订并没有补回重构成功，不能归于latent组合。
