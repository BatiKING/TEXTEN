grid_layout ='''+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+
|      |      |      |      |      |      |
|      |      |      |      |      |      |
+------+------+------+------+------+------+'''


p1_indicator = 'P1'
p1_symbol= '██'
p2_indicator = 'P2'
p2_symbol= '██'
first_line_offset = 47
second_line_offset = first_line_offset + 44
one_column_offset = 7
one_row_offset = 132

# coordinates = [2,3]
# line_1_position = first_line_offset + ((6 - coordinates[1]) * one_row_offset) + (coordinates[0] * one_column_offset)
# line_2_position = second_line_offset + ((6 - coordinates[1]) * one_row_offset) + (coordinates[0] * one_column_offset)
# grid_layout = grid_layout[:line_1_position] + p1_indicator + grid_layout[line_1_position + len(p1_indicator):line_2_position] + p1_symbol + grid_layout[line_2_position + len(p1_symbol):]


# coordinates = [3,3]
# line_1_position = first_line_offset + ((6 - coordinates[1]) * one_row_offset) + (coordinates[0] * one_column_offset)
# line_2_position = second_line_offset + ((6 - coordinates[1]) * one_row_offset) + (coordinates[0] * one_column_offset)
# grid_layout = grid_layout[:line_1_position] + p2_indicator + grid_layout[line_1_position + len(p2_indicator):line_2_position] + p2_symbol + grid_layout[line_2_position + len(p2_symbol):]

#print(grid_layout)

def position_characters_on_grid(grid_string, player1_character, player2_character):
    def calc_line_positions(coordinates):
        line_1_position = first_line_offset + ((6 - coordinates[1]) * one_row_offset) + (coordinates[0] * one_column_offset)
        line_2_position = second_line_offset + ((6 - coordinates[1]) * one_row_offset) + (coordinates[0] * one_column_offset)
        return line_1_position, line_2_position
    l1_pos, l2_pos = calc_line_positions([player1_character.x_pos, player1_character.y_pos])
    grid_string = grid_string[:l1_pos] + p1_indicator + grid_string[l1_pos + len(p1_indicator):l2_pos] + p1_symbol + grid_string[l2_pos + len(p1_symbol):]
    
    l1_pos, l2_pos = calc_line_positions([player2_character.x_pos, player2_character.y_pos])
    grid_string = grid_string[:l1_pos] + p2_indicator + grid_string[l1_pos + len(p2_indicator):l2_pos] + p2_symbol + grid_string[l2_pos + len(p2_symbol):]

    return grid_string

