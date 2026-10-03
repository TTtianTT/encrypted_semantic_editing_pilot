# 情感语言结构续步案例审阅

这是助手对固定首个test世界emotion_0120的六个P/forward案例的文字审阅，覆盖42/43/44和多对象结构4、历史直接引语结构5。选择不依赖输出成功；它们不是六个独立内容世界，也不是独立人工总体标签。完整原始文本、gold、评分、mask、三个路径及文件哈希见LANGUAGE_FIXED_CONTINUATION_CASES.jsonl。该文件另保留其他已执行P结构和反向/逆操作固定案例；它们不自动继承本审阅标签。

六例第一步均完整正确地表达Alice dislikes the parcel，Henry的neutral评价、颜色blue及9 copies均保持；结构4的Alice dislikes the box和结构5的David历史原话I dislike the parcel也保持。第二步应只把Alice对parcel改成neutral。六例gold-reencode和decode–reencode第二步都完整正确。

|seed|结构|纯latent第二步的可见错误|
|---|---|---|
|42|多对象4|只剩Focus头，目标评价、非目标评价及客观事实正文均缺失。|
|42|引语5|Focus后重复neutral/neutral数字片段，未正常结束；完整目标/非目标内容及引语未保留。|
|43|多对象4|Alice likes the parcel，预期neutral；Henry评价、box评价和客观事实缺失。|
|43|引语5|Alice likes the parcel，预期neutral；Henry评价、客观事实及历史引语缺失。|
|44|多对象4|Alice is strongly liked by the parcel，评价方向反转；Alice对box从dislikes变成neutral。Henry neutral、blue和9 copies仍在。被动句可以合乎一般英语语法，原controlled grammar的失败不能代替该语义分析。|
|44|引语5|仍为Alice dislikes the parcel，等级未前进；Henry评价、客观事实及历史引语缺失。|

三种子P的两个结构第二步均为0/96，第一步96/96；第二步重编码两路径均96/96。多对象两条重编码路径四步均96/96；引语第四步为92/96、95/96、93/96，存在基本原子/生成失败的反例，不能称为始终成功。三条轨迹共用32个内容世界，步/方向不是独立样本。

mask差异及重编码表示变化保留；这些行为案例不识别唯一失败机制。该审阅只证明这些具体语言结构也出现当前正确后无法继续，且失败可同时涉及等级、参与者/对象绑定、作用范围和正文丢失。
