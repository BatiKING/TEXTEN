#Definition of a single Texten Game/match between two players
# from dis import dis
# from select import select
# from tkinter import Y
from audioop import add
import grid_layout

class TextenGame:
    def __init__(self, game_id, p1_id, p2_id, p1_name, p2_name, p1_room_id, p2_room_id, general_room_id) -> None:
        self.game_id = game_id
        self.p1_id = p1_id
        self.p2_id = p2_id
        self.p1_name = p1_name
        self.p2_name = p2_name
        self.p1_room_id = p1_room_id
        self.p2_room_id = p2_room_id
        self.general_room_id = general_room_id
        self.turn_counter = 0
        self.stage = TextenStage(self.p1_room_id, self.p2_room_id)
    
    def handle_message(self, message):
        #response = f"Message delivered to game id {self.game_id}, from room_id {message.channel.id}"
        message_params = message.content.split(' ')
        print(message_params)
        if len(message_params) == 4:
            p1_x = int(message_params[0])
            p1_y = int(message_params[1])
            p2_x = int(message_params[2])
            p2_y = int(message_params[3])
            self.stage.player1_character.set_position(p1_x,p1_y)
            self.stage.player2_character.set_position(p2_x,p2_y)
        ss_dir = message.content
        self.stage.update_facing_directions(self.stage.player1_character, self.stage.player2_character)
        pre_ss_p1_position = self.stage.player1_character.get_position()
        pre_ss_p2_position = self.stage.player2_character.get_position() 
        ss_to_position = self.stage.try_sidestep(self.stage.player1_character, self.stage.player2_character, ss_dir)
        additional_message = ''
        if ss_to_position is None:
            additional_message = "\n p1 couldn't sidestep"
        else:
            self.stage.player1_character.set_position(ss_to_position[0], ss_to_position[1])
        #response = f"p1_pre_ss = {pre_ss_p1_position}, p2_pre_ss = {pre_ss_p2_position}, - SS coordinate = {ss_to_position} - p1_post_ss = {self.stage.player1_character.get_position()}, p2_post_ss = {self.stage.player2_character.get_position()}"
        response = "```\n" + grid_layout.position_characters_on_grid(grid_layout.grid_layout, self.stage.player1_character, self.stage.player2_character) + "```" + additional_message
        return response

class TextenStage:
    def __init__(self, player1_room_id, player2_room_id, width=6, height=7) -> None:
        self.width = width
        self.height = height
        self.player1_character = TextenPlayerCharacter(player1_room_id, 2,3)
        self.player2_character = TextenPlayerCharacter(player2_room_id, 3,3)
        self.update_facing_directions(self.player1_character, self.player2_character)

    def calculate_distance_between_characters(self, player1_character, player2_character):
        distance_between_characters = max(abs(player1_character.x_pos - player2_character.x_pos), abs(player1_character.y_pos - player2_character.y_pos)) - 1
        return distance_between_characters

    def calculate_distance_between_characters_manual(self, p1_x_pos, p1_y_pos, player2_character):
        distance_between_characters = max(abs(p1_x_pos - player2_character.x_pos), abs(p1_y_pos - player2_character.y_pos)) - 1
        return distance_between_characters

    def update_facing_directions(self, p1_character, p2_character):
        p1_directions = []
        p2_directions = []
        if p1_character.x_pos < p2_character.x_pos:
            p1_directions.append('right')
            p2_directions.append('left')
        elif p1_character.x_pos > p2_character.x_pos:
            p1_directions.append('left')
            p2_directions.append('right')

        if p1_character.y_pos < p2_character.y_pos:
            p1_directions.append('up')
            p2_directions.append('down')
        elif p1_character.y_pos > p2_character.y_pos:
            p1_directions.append('down')
            p2_directions.append('up')

        self.player1_character.set_facing_directions(p1_directions)
        self.player2_character.set_facing_directions(p2_directions)
        return True

    def try_sidestep(self, moving_character, waiting_character, ss_direction):
        distance = self.calculate_distance_between_characters(moving_character, waiting_character)
        waiting_char_position = {'x' : waiting_character.x_pos, 'y' : waiting_character.y_pos}
        moving_character_position = {'x' : moving_character.x_pos, 'y' : moving_character.y_pos}
        grid = [[x,y] for x in range(6) for y in range(7)]
        valid_positions = []
        for field in grid:
            if distance == self.calculate_distance_between_characters_manual(field[0], field[1], waiting_character):
                if abs(field[0] - moving_character_position['x']) <= 1 and abs(field[1] - moving_character_position['y']) <= 1 and (field[0], field[1]) != (moving_character_position['x'], moving_character_position['y']): 
                    valid_positions.append(field)
        print(distance)
        print(valid_positions)

        #BELOW CONDITION CHECKS WHICH SS COORDINATE IS THE FURTHEST AWAY FROM THE WAITING CHARACTER, AND REMOVES IT - THIS TO MAKE SURE THE SSing CHARACTER DOES ROUND CORNER MOVEMENT WHEN SSing FROM FAR AWAY
        if distance != 0 and len(valid_positions) > 2:             
            most_far_away_coordinate = []
            max_diff = 0
            for coordinates in valid_positions:
                x_diff = abs(coordinates[0] - waiting_char_position['x'])
                y_diff = abs(coordinates[1] - waiting_char_position['y'])
                if x_diff + y_diff > max_diff:
                    max_diff = x_diff + y_diff
                    most_far_away_coordinate = coordinates
            valid_positions.remove(most_far_away_coordinate)
            print(f"distance bigger than 0 - removing stuff - remaining positions = {valid_positions}")
        #BELOW CONDITION CHECK WHICH SS COORDINATE IS THE FURTHEST AWAY FROM THE MOVING CHARACTER AND REMOVES IT - THIS TO MAKE SURE THAT IF CHARS ARE NEXT TO EACHOTHER, THEY DO FULL CIRCLE WHEN SSing    
        elif distance == 0 and len(valid_positions) > 2: 
            for_removal = []                                 
            for coordinates in valid_positions:
                x_diff = abs(coordinates[0] - moving_character_position['x'])
                y_diff = abs(coordinates[1] - moving_character_position['y'])
                print(f"x_diff + y_diff = {x_diff + y_diff} and coords = {coordinates}")
                if x_diff + y_diff > 1:
                    for_removal.append(coordinates)
            valid_positions = [x for x in valid_positions if x not in for_removal]
            
            print(f"0 distance - removing stuff - remaining positions = {valid_positions}")

        print(moving_character.facing_directions)
        if ss_direction == 'left':
            if ['right', 'up'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] < moving_character_position['x'] or coordinates[1] > moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['right', 'down'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] > moving_character_position['x'] or coordinates[1] > moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['left', 'up'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] < moving_character_position['x'] or coordinates[1] < moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['left', 'down'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] > moving_character_position['x'] or coordinates[1] < moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['left'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[1] < moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['right'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[1] > moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['up'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] < moving_character_position['x']:
                        print(coordinates)
                        return coordinates
            elif ['down'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] > moving_character_position['x']:
                        print(coordinates)
                        return coordinates                                         
        elif ss_direction == 'right':
            if ['right', 'up'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] > moving_character_position['x'] or coordinates[1] < moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['right', 'down'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] < moving_character_position['x'] or coordinates[1] < moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['left', 'up'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] > moving_character_position['x'] or coordinates[1] > moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['left', 'down'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] < moving_character_position['x'] or coordinates[1] > moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['left'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[1] > moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['right'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[1] < moving_character_position['y']:
                        print(coordinates)
                        return coordinates
            elif ['up'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] > moving_character_position['x']:
                        print(coordinates)
                        return coordinates
            elif ['down'] == moving_character.facing_directions:
                for coordinates in valid_positions:
                    if coordinates[0] < moving_character_position['x']:
                        print(coordinates)
                        return coordinates
            

class TextenPlayerCharacter:
    def __init__(self, player_room_id, x_pos, y_pos ,hp=180) -> None:
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.player_room_id = player_room_id
        self.hp = hp
        self.facing_directions = []
    
    def get_position(self):
        return [self.x_pos, self.y_pos]
    
    def set_position(self, x_pos, y_pos):
        self.x_pos = x_pos
        self.y_pos = y_pos
        return True

    def set_facing_directions(self, directions):
        self.facing_directions = directions

    def get_facing_directions(self):
        return self.facing_directions

class TextenMove:
    def __init__(self) -> None:
        pass

#Definition of a Challenge sent from one player to the other.
class TextenChallenge:
    def __init__(self) -> None:
        pass

#Definition of the main Game Manager - there will only be one instance of this object, and it will manage the individual matches and challenges
#Maybe try to implement Singleton in the future...
class GameManager:
    def __init__(self) -> None:
        self.all_games = {}
        self.all_challenges = []


    def create_new_game(self, game_id,p1_id, p2_id, p1_name, p2_name, p1_room_id, p2_room_id, general_room_id):        
        self.all_games[game_id] = TextenGame(game_id,p1_id, p2_id, p1_name, p2_name, p1_room_id, p2_room_id, general_room_id)
        return True

    def get_game_object(self, game_id):
        if self.check_if_game_exist(game_id):
            return self.all_games[game_id]
        else:
            return None
    
    def delete_game_object(self, game_id):
        if self.check_if_game_exist(game_id):
            del self.all_games[game_id]
            return True
        else:
            return False

    def create_new_challenge(self, challenge_id):
        self.all_challenges.append(challenge_id)
        return True
    
    def check_if_challenge_exist(self, challenge_id):
        return challenge_id in self.all_challenges

    def delete_challenge(self, challenge_id):
        if self.check_if_challenge_exist(challenge_id):
            self.all_challenges.remove(challenge_id)
            return True
        else:
            return False

    def check_if_game_exist(self, game_id):       
        if game_id in self.all_games.keys():
            return True
        else:
            return False

    def create_challenge_id(self, guild_id, p1_id, p2_id):
        if p1_id > p2_id:
            return f"{guild_id}_{p1_id}_{p2_id}"
        else:
            return f"{guild_id}_{p2_id}_{p1_id}"

    def create_game_id(self, guild_id, p1_id, p2_id):
        if p1_id > p2_id:
            return f"{guild_id}_{p1_id}_{p2_id}"
        else:
            return f"{guild_id}_{p2_id}_{p1_id}"

    def check_if_message_sent_from_game_room(self, room_id):
        for game in self.all_games.values():
            if game.p1_room_id == room_id or game.p2_room_id == room_id:
                return game.game_id
        return None

    def handle_game_room_message(self, game_id, message):
       response = self.all_games[game_id].handle_message(message)
       return response