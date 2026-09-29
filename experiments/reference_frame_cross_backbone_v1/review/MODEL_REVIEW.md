# 模型复核记录（不是真人审核）

复核方式：执行者阅读下列便利选取的原始输出及同记录对照，检查自动判定对应的具体文本。没有重新打分，没有修改parser，没有把这些例子当作总体准确率估计。预选20世界的盲审包中human_label和human_notes保持空白。

- FLAN-T5-base，calibration A首个未通过视图：完整的否定计划记录被输出成“No”。这条确有大量内容遗漏；不能由这一例推断所有自动未决都属于同一种错误。
- T5Gemma2 270M-270M，同一校准正文：出现unused token和重复Record/Record date行，正文未保留。这是当前固定无编辑接口的重构失败例，不是经过任务训练的编辑失败例。
- FLAN-T5-large，B包装，Bob的取消计划记录：输出仅缺2026-11-08后的句点，其余字符串保持。该条自动未决来自严格header格式，不能称作已证实事实错误。固定原句920视图中有9条这种仅句点差异，另13条只剩作者/记录日、缺失正文，见punctuation_diagnostic.json。保留原自动分数和未准入结论，没有回填人为成功标签。
- BART G1，cross_v1_test_iid_0000，plus_plus：第一步把two days ago改为three days ago并保留否定、eight parcels及角色；第二步变为大量重复的two/three/four/Author片段，人物和事件正文丢失。此例的未决伴随实际退化。G1重编码和G3纯链在同记录中得到正确four days ago，完整轨迹可核验。
- BART G3，cross_v1_test_template_ood_0005，plus_person：取消计划、数量和角色词仍出现，但日期句与证据说明被that连接，随后又重复证据说明。该例自动未决；本复核不把残留词语视为事实与作用域已经全部保持，也不擅自改成确定的状态损坏。
- T5Gemma IT G1，cross_v1_test_iid_0000，plus_plus：第一步正确，第二步只有“Author:”。这里未决确实伴随正文丢失，不只是分隔符格式变化。
- T5Gemma IT G1，cross_v1_test_iid_0016，minus_minus：源记录为seven books；第一步仍为seven books，第二步变为eight books，日期也不正确。数量变化是已解析且可直接读出的事实损坏。
- T5Gemma IT G1，cross_v1_test_iid_0037，plus_minus：five parcels在第二步变为six parcels，同时没有回到正确的日期表达。不能把往返算子仅看成输出流畅即可通过。
- T5Gemma IT G1，cross_v1_test_iid_0000，person_plus：第一步身份改写正确；第二步把tomorrow改为yesterday，正确一步应为today。主体、否定和数量看似保留，日期控制仍失败。

- T5Gemma IT G3，cross_v1_test_template_ood_0078，plus_plus：正确轨迹应为in two days→tomorrow→today，实际第一步为in three days，第二步为today。因此终点正确而全轨迹错误；第一步属于其他错误日期，不能归类成提前到达两步终点。
- T5Gemma IT G3，cross_v1_test_iid_0000，plus_person：时间一步先得到正确yesterday；随后人称一步虽然改成Grace's，却把日期恢复成today。G1同记录两步均正确。这里是跨操作组合损坏日期，不能仅凭身份已改正确算成功。
- T5Gemma IT G3，cross_v1_test_iid_0004，person_plus：身份一步正确；时间一步仍保留today，正确应为yesterday。G1同记录成功，清楚显示能力取舍。
- T5Gemma IT G3，cross_v1_test_iid_0000，plus3：实际tomorrow→today→yesterday→yesterday，前两次正确，第三次没有继续移动参考日。不能把流畅、保留角色和数量的输出当作三步转换正确。

以上样本均来自冻结输出文件。完整便利案例由analyze.py导出，类别不存在时明确写未观察到，不强凑案例。复核只描述这些可读文本，没有覆盖全部未决输出，没有人类标签，也未改变任何自动主率。
