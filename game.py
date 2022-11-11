#Definition of a single Texten Game/match between two players
# from dis import dis
# from select import select
# from tkinter import Y
from audioop import add
import grid_layout
import random



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
        self.stage = TextenStage(self.p1_room_id, p1_id, self.p2_room_id, p2_id)
        # self.current_turn_player_id = self.coin_flip()
        self.p1_action_taken_current_turn = False
        self.p1_action = TextenAction(player_id=p1_id, player_character=self.stage.player1_character)
        self.p2_action_taken_current_turn = False
        self.p2_action = TextenAction(player_id=p2_id, player_character=self.stage.player2_character)
        self.command_dict = {
            'ssr': self.sidestep,
            'ssl': self.sidestep,
            'sidestep': self.sidestep,
            'ss': self.sidestep,
            'backdash': self.backdash,
            'bd': self.backdash,
            'bb': self.backdash,
            'frontdash': self.frontdash,
            'fd': self.frontdash,
            'ff': self.frontdash,
            'duck': self.duck,
            'crouch': self.duck,
            'db': self.duck,
            'd': self.duck,
            'position': self.set_players_position,
        }
    def coin_flip(self):
        if random.randint(0,1):
            return self.p1_id
        else:
            return self.p2_id
            
    def get_match_start_message(self):
        # if self.current_turn_player_id == self.p1_id:
        #     return f"Coinflip: HEADS win! {self.p1_name} goes first!\nFIGHT!"
        # else:
        #     return f"Coinflip: TAILS win! {self.p2_name} goes first!\nFIGHT!"
        return f"FIGHT!"

    def handle_message(self, message):
        """This method should return a tuple, response_message and send_to_all_rooms, -
         send_to_all_rooms is meant to inform main app if this response should be sent to all room chats, or if it should only go to sender"""

        if (message.author.id == self.p1_id and self.p1_action_taken_current_turn) or (message.author.id == self.p2_id and self.p2_action_taken_current_turn):
            #response = "```\n" + grid_layout.position_characters_on_grid(grid_layout.grid_layout, self.stage.player1_character, self.stage.player2_character) + "```" + "Wait for the next turn"
            response = "Wait for the next turn"
            send_to_all_rooms = False
            return response, send_to_all_rooms


        
        message_params = message.content.split(' ')
        player_action = self.p1_action if message.author.id == self.p1_id else self.p2_action

        if func := self.command_dict.get(message_params[0].lower()):
            success = func(player_action, *message_params)
            if not success:
                return "Incorrect input - type a valid command", False
        else:
            return "Incorrect input - type a valid command", False
            

        if message.author.id == self.p1_id:
            self.p1_action_taken_current_turn = True
        elif message.author.id == self.p2_id:
            self.p2_action_taken_current_turn = True
        
        #this additional message is temporary
        additional_message = ''
        #response = f"p1_pre_ss = {pre_ss_p1_position}, p2_pre_ss = {pre_ss_p2_position}, - SS coordinate = {ss_to_position} - p1_post_ss = {self.stage.player1_character.get_position()}, p2_post_ss = {self.stage.player2_character.get_position()}"
        
        
        #If both players took their turns, reset the "turn taken" flags and draw the stage 
        if self.p1_action_taken_current_turn and self.p2_action_taken_current_turn:
            self.p1_action_taken_current_turn = False
            self.p2_action_taken_current_turn = False
            response = "```\n" + grid_layout.position_characters_on_grid(grid_layout.grid_layout, self.stage.player1_character, self.stage.player2_character) + "```" + additional_message
            send_to_all_rooms = True
            return response, send_to_all_rooms

        return "Wait for your opponents move", False

    def set_players_position(self, action, *message_params):
        print(message_params)
        if len(message_params) > 4:
            p1_x = int(message_params[-4])
            p1_y = int(message_params[-3])
            p2_x = int(message_params[-2])
            p2_y = int(message_params[-1])
            self.stage.player1_character.set_position(p1_x,p1_y)
            self.stage.player2_character.set_position(p2_x,p2_y)
            return True
        return False

    def sidestep(self, action, *args):
        ss_dir_dict = {
            'ssl': 'left',
            'l': 'left',
            'left': 'left',
            'ssr': 'right',
            'right': 'right',
            'r': 'right'
        }
        ss_dir = ss_dir_dict.get(args[-1].lower())
        if ss_dir:
            self.stage.update_facing_directions(self.stage.player1_character, self.stage.player2_character)
            pre_ss_p1_position = self.stage.player1_character.get_position()
            pre_ss_p2_position = self.stage.player2_character.get_position() 
            if action.player_id == self.p1_id:
                ss_to_position = self.stage.try_sidestep(action.player_character, self.stage.player2_character, ss_dir)
            elif action.player_id == self.p2_id:
                ss_to_position = self.stage.try_sidestep(action.player_character, self.stage.player1_character, ss_dir)
            additional_message = ''
            if ss_to_position is None:
                additional_message = f"\n {action.player_id} couldn't sidestep"
            else:
                action.player_character.set_position(ss_to_position[0], ss_to_position[1])
            
            return True
        else:
            return False

        

    def backdash(self, action, *args):
        self.stage.update_facing_directions(self.stage.player1_character, self.stage.player2_character)
        if action.player_id == self.p1_id:
            bd_to_position = self.stage.try_backdash(action.player_character, self.stage.player2_character)
        elif action.player_id == self.p2_id:
            bd_to_position = self.stage.try_backdash(action.player_character, self.stage.player1_character)
        
        return True
    
    
    def frontdash(self, action):
        pass

    def duck(self, action):
        pass

class TextenStage:
    def __init__(self, player1_room_id, player1_id, player2_room_id, player2_id, width=6, height=7) -> None:
        self.player1_id = player1_id
        self.player2_id = player2_id
        self.width = width
        self.height = height
        self.player1_character = TextenPlayerCharacter(player1_room_id, player1_id, 2,3)
        self.player2_character = TextenPlayerCharacter(player2_room_id, player2_id, 3,3)
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

    def try_backdash(self, moving_character, waiting_character):
        distance = self.calculate_distance_between_characters(moving_character, waiting_character)
        waiting_char_position = {'x' : waiting_character.x_pos, 'y' : waiting_character.y_pos}
        moving_character_position = {'x' : moving_character.x_pos, 'y' : moving_character.y_pos}
        grid = [[x,y] for x in range(6) for y in range(7)]
        valid_positions = []
        for field in grid:
            if self.calculate_distance_between_characters_manual(field[0], field[1], moving_character) == 0:
                if self.calculate_distance_between_characters_manual(field[0], field[1], waiting_character) > distance: 
                    valid_positions.append(field)
        if len(valid_positions) > 0:
            list_of_cross_products = [abs((field[1] - waiting_char_position['y']) * (moving_character_position['x'] - waiting_char_position['x']) - (field[0] - waiting_char_position['x']) * (moving_character_position['y'] - waiting_char_position['y'])) for field in valid_positions]
        
        cross_product_and_position_list = zip(list_of_cross_products, valid_positions)
        best_bd_coordinate = sorted(list(cross_product_and_position_list))[0]
        print(distance)
        print(valid_positions)    
        print(f"temp calc list {list_of_cross_products}")
        print(best_bd_coordinate)

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
    def __init__(self, player_room_id, player_id, x_pos, y_pos ,hp=180) -> None:
        self.player_id = player_id
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

class TextenAction:
    def __init__(self, player_id, player_character, movement=False, attack=False, backdash=False, sidestep=False, frontdash=False, duck=False, low_crush=False, high_crush=False, block=False, backswing=False, homing=False, damage=0, range=0) -> None:
        self.player_id = player_id
        self.player_character = player_character
        self.movement = movement
        self.attack = attack
        self.backdash = backdash
        self.sidestep = sidestep
        self.frontdash = frontdash
        self.duck = duck
        self.low_crush = low_crush
        self.high_crush = high_crush
        self.block = block
        self.backswing = backswing
        self.homing = homing
        self.damage = damage
        self.range = range


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
        return self.all_games[game_id]

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