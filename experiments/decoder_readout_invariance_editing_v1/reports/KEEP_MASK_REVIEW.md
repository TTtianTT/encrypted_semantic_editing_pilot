# 内容位置人工抽查样本

16个固定train world；只保护 object/event_object/status/color/quantity 语义槽位。日期变化、时态/人称agreement及必要语法位置、标点与BOS/EOS排除。仅tokenizer运行，无模型前向。待人工抽查，不声称已有人类核验。

## drie_013a626fe072d215 plus

Source: The sensor event is dated today. Its status is cancelled. The sensor is green. There are 6 copies.

Target: The sensor event is dated yesterday. Its status is cancelled. The sensor is green. There are 6 copies.

Keep tokens: 2='sensor' (object), 11='cancelled' (status), 14='sensor' (object), 16='green' (color), 20='6' (quantity)

## drie_c5fdacb609ac92cd minus

Source: The lamp event is dated today. Its status is completed. The lamp is white. There are 2 copies.

Target: The lamp event is dated tomorrow. Its status is completed. The lamp is white. There are 2 copies.

Keep tokens: 2='lamp' (object), 11='completed' (status), 14='lamp' (object), 16='white' (color), 20='2' (quantity)

## drie_21b85f778b13aef3 plus

Source: The cup event is dated today. Its status is completed. The cup is blue. There are 2 copies.

Target: The cup event is dated yesterday. Its status is completed. The cup is blue. There are 2 copies.

Keep tokens: 2='cup' (object), 11='completed' (status), 14='cup' (object), 16='blue' (color), 20='2' (quantity)

## drie_7bfd1901f2d82f26 minus

Source: The lamp event is dated today. Its status is completed. The lamp is green. There are 7 copies.

Target: The lamp event is dated tomorrow. Its status is completed. The lamp is green. There are 7 copies.

Keep tokens: 2='lamp' (object), 11='completed' (status), 14='lamp' (object), 16='green' (color), 20='7' (quantity)

## drie_17a0a6b03c5066a5 plus

Source: The book event is dated today. Its status is planned. The book is blue. There are 5 copies.

Target: The book event is dated yesterday. Its status is planned. The book is blue. There are 5 copies.

Keep tokens: 2='book' (object), 11='planned' (status), 14='book' (object), 16='blue' (color), 20='5' (quantity)

## drie_dd0f1c98756ff57e minus

Source: The ticket event is dated today. Its status is planned. The ticket is green. There are 9 copies.

Target: The ticket event is dated tomorrow. Its status is planned. The ticket is green. There are 9 copies.

Keep tokens: 2='ticket' (object), 11='planned' (status), 14='ticket' (object), 16='green' (color), 20='9' (quantity)

## drie_c422b41d571884e2 plus

Source: The cup event is dated today. Its status is completed. The cup is black. There are 5 copies.

Target: The cup event is dated yesterday. Its status is completed. The cup is black. There are 5 copies.

Keep tokens: 2='cup' (object), 11='completed' (status), 14='cup' (object), 16='black' (color), 20='5' (quantity)

## drie_edbe2cb528222b4a minus

Source: The parcel event is dated today. Its status is cancelled. The parcel is red. There are 9 copies.

Target: The parcel event is dated tomorrow. Its status is cancelled. The parcel is red. There are 9 copies.

Keep tokens: 2='parcel' (object), 11='cancelled' (status), 14='parcel' (object), 16='red' (color), 20='9' (quantity)

## drie_a2280432de2c711d plus

Source: The key event is dated today. Its status is planned. The key is white. There are 2 copies.

Target: The key event is dated yesterday. Its status is planned. The key is white. There are 2 copies.

Keep tokens: 2='key' (object), 11='planned' (status), 14='key' (object), 16='white' (color), 20='2' (quantity)

## drie_4ae63971af505285 minus

Source: The box event is dated today. Its status is planned. The box is blue. There are 5 copies.

Target: The box event is dated tomorrow. Its status is planned. The box is blue. There are 5 copies.

Keep tokens: 2='box' (object), 11='planned' (status), 14='box' (object), 16='blue' (color), 20='5' (quantity)

## drie_594d650d276507ca plus

Source: The sensor event is dated today. Its status is planned. The sensor is black. There is 1 copy.

Target: The sensor event is dated yesterday. Its status is planned. The sensor is black. There is 1 copy.

Keep tokens: 2='sensor' (object), 11='planned' (status), 14='sensor' (object), 16='black' (color), 20='1' (quantity)

## drie_f1942e7cfb9f1b0c minus

Source: The lamp event is dated today. Its status is planned. The lamp is white. There are 5 copies.

Target: The lamp event is dated tomorrow. Its status is planned. The lamp is white. There are 5 copies.

Keep tokens: 2='lamp' (object), 11='planned' (status), 14='lamp' (object), 16='white' (color), 20='5' (quantity)

## drie_3f692f40b7550e88 plus

Source: The book event is dated today. Its status is planned. The book is green. There are 4 copies.

Target: The book event is dated yesterday. Its status is planned. The book is green. There are 4 copies.

Keep tokens: 2='book' (object), 11='planned' (status), 14='book' (object), 16='green' (color), 20='4' (quantity)

## drie_29261698ee8d4652 minus

Source: The cup event is dated today. Its status is cancelled. The cup is black. There are 5 copies.

Target: The cup event is dated tomorrow. Its status is cancelled. The cup is black. There are 5 copies.

Keep tokens: 2='cup' (object), 11='cancelled' (status), 14='cup' (object), 16='black' (color), 20='5' (quantity)

## drie_dfc05856f7d46683 plus

Source: The cup event is dated today. Its status is planned. The cup is blue. There are 7 copies.

Target: The cup event is dated yesterday. Its status is planned. The cup is blue. There are 7 copies.

Keep tokens: 2='cup' (object), 11='planned' (status), 14='cup' (object), 16='blue' (color), 20='7' (quantity)

## drie_7ec9c4e11532e597 minus

Source: The box event is dated today. Its status is planned. The box is black. There are 8 copies.

Target: The box event is dated tomorrow. Its status is planned. The box is black. There are 8 copies.

Keep tokens: 2='box' (object), 11='planned' (status), 14='box' (object), 16='black' (color), 20='8' (quantity)

