# BART固定句序/锚点案例审阅

审阅POSITION_FIXED_REVIEW_CASES中的seed42、plus、各领域固定首个test世界和指定内点状态的五对输入（情感分多对象和Narrator/引语两对）。选择不依赖输出成功，原文本、gold、评分和文件哈希均保留。不是独立人工总体标签；其余seed/方向不继承这些文字判断。四种结构在BART的所有正式seed均未通过冻结dev准入，本记录是原子作用范围/生成案例，不是latent组合失败率。

- 时间：外部today应变为yesterday，历史引语three days from now必须保留。两种顺序均保持外部today，却将历史引语改为two days from now；另有events is或event are一致错误、ISO日期改成斜线格式。引语内容的改变直接证明这些输出违反了规定的锚点/历史原话范围。斜线日期本身可能表达相同日期，不能自动当成日期身份错误。dev重构原有限分数为0，因此整体能力不足/解析边界与作用范围错误同时存在，不能归于连续组合。
- 空间：目标在前时输出to my left符合该操作，颜色句parcel变为package被旧字段判为非目标失败；parcel/package可能是合理同义，不能据此独立证实对象身份改变。目标在后时保留A的in front of me，删掉固定Emma观点并添加I am on the back side。原评分未成功；这段新增表达的对象/观察者绑定不能靠单个方向词确定。
- 情感多对象：目标在前时目标parcel提高为likes、Henry neutral和box dislikes保持，但增加了Jane评价片段。目标在后时parcel目标仍neutral，而非目标box从dislikes变成neutral。后者是明确的错误对象范围。前者的raw target/preserved/scope为True、controlled grammar与综合success为False：已识别预期槽位保持不保证不存在额外内容，不能把这个scope分项单独当成完整作用范围正确证明。
- 情感Narrator/引语：目标在前和引语在前均保留外部I am neutral，未提高等级；引语在前还把David原话I dislike改成I like。这是明确的历史观点保护失败。Narrator保持Alice，不将观点改写错误误称为Narrator身份换人。
- 人称：目标在前正确切换为Speaker Carol/Listener Henry，事件Grace gives me your parcel身份也正确，但历史引语丢失并添加There is 4 copies；目标在后产生空输出。区分事件保持、历史内容缺失和一致错误，不把所有失败统一叫作参与者绑定错误。

有限自动评分的成功判定同时要求预期槽、完整受控句式和正常结束；分项target/preserved/scope只描述其可识别字段，陌生附加内容可能被完整性条件拒绝而未出现在分项字段。上述额外Jane案例不是综合成功的假阳性。原正式分数、准入、checkpoint和cohort不变。更开放同义表达或日期格式仍可能产生假阴性，未将未知输出都标为独立证实的语义错误。
