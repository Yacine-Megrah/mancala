import pygame
import sys
from copy import deepcopy
from math import inf

class MancalaBoard:
    def __init__(self):
        self.board = {
            'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4, 'F': 4,
            'G': 4, 'H': 4, 'I': 4, 'J': 4, 'K': 4, 'L': 4,
            '1': 0, '2': 0  # Stores
        }
        
        self.player1_pits = ('A', 'B', 'C', 'D', 'E', 'F')
        self.player2_pits = ('G', 'H', 'I', 'J', 'K', 'L')
        
        # Map opposite pits
        self.opposite_pits = {
            'A': 'L', 'B': 'K', 'C': 'J', 'D': 'I', 'E': 'H', 'F': 'G',
            'G': 'F', 'H': 'E', 'I': 'D', 'J': 'C', 'K': 'B', 'L': 'A'
        }
        
        # Map next pit in sequence
        self.next_pit = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': '1',
            '1': 'L', 'L': 'K', 'K': 'J', 'J': 'I', 'I': 'H', 'H': 'G',
            'G': '2', '2': 'A'
        }
    
    def possibleMoves(self, player):
        if player == "player1":
            return [pit for pit in self.player1_pits if self.board[pit] > 0]
        else:
            return [pit for pit in self.player2_pits if self.board[pit] > 0]
    
    def doMove(self, player, pit):
        if (player == "player1" and pit not in self.player1_pits) or \
           (player == "player2" and pit not in self.player2_pits):
            return False
        
        seeds = self.board[pit]
        if seeds == 0:
            return False
        
        self.board[pit] = 0
        current_pit = pit
        
        while seeds > 0:
            current_pit = self.next_pit[current_pit]
            # Skip opponent's store
            if (player == "player1" and current_pit == '2') or \
               (player == "player2" and current_pit == '1'):
                continue
            
            self.board[current_pit] += 1
            seeds -= 1
        
        # Check for capture
        if current_pit in (self.player1_pits if player == "player1" else self.player2_pits):
            if self.board[current_pit] == 1:  # Last seed was placed in an empty pit
                opposite_pit = self.opposite_pits[current_pit]
                if self.board[opposite_pit] > 0:
                    store = '1' if player == "player1" else '2'
                    self.board[store] += self.board[opposite_pit] + 1
                    self.board[opposite_pit] = 0
                    self.board[current_pit] = 0
        
        return True

class Game:
    def __init__(self, human_side="player1"):
        self.state = MancalaBoard()
        self.playerSide = {
            1: "player1" if human_side == "player2" else "player2",  # Computer
            -1: human_side  # Human
        }
    
    def gameOver(self):
        player1_empty = all(self.state.board[pit] == 0 for pit in self.state.player1_pits)
        player2_empty = all(self.state.board[pit] == 0 for pit in self.state.player2_pits)
        
        if player1_empty or player2_empty:
            # Collect remaining seeds
            for pit in self.state.player1_pits:
                self.state.board['1'] += self.state.board[pit]
                self.state.board[pit] = 0
            for pit in self.state.player2_pits:
                self.state.board['2'] += self.state.board[pit]
                self.state.board[pit] = 0
            return True
        return False
    
    def findWinner(self):
        score1 = self.state.board['1']
        score2 = self.state.board['2']
        if score1 > score2:
            return "player1", score1
        elif score2 > score1:
            return "player2", score2
        else:
            return "tie", score1
    
    def evaluate(self):
        computer_store = '1' if self.playerSide[1] == "player1" else '2'
        human_store = '2' if self.playerSide[-1] == "player2" else '1'
        return self.state.board[computer_store] - self.state.board[human_store]

class MancalaGUI:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 400
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mancala")
        
        self.font = pygame.font.Font(None, 36)
        self.game = Game("player1")  # Human plays as player1
        self.running = True
        
        # Define pit positions
        self.pit_radius = 40
        self.store_height = 160
        self.store_width = 60
        
        # Calculate pit positions
        self.calculate_positions()
    
    def calculate_positions(self):
        # Store positions
        self.store_positions = {
            '1': (self.width - 40, self.height // 2),  # Right store
            '2': (40, self.height // 2)                # Left store
        }
        
        # Pit positions
        pit_spacing = (self.width - 160) // 6
        self.pit_positions = {}
        
        # Player 1 pits (bottom)
        for i, pit in enumerate(self.game.state.player1_pits):
            self.pit_positions[pit] = (120 + i * pit_spacing, self.height - 80)
        
        # Player 2 pits (top)
        for i, pit in enumerate(reversed(self.game.state.player2_pits)):
            self.pit_positions[pit] = (120 + i * pit_spacing, 80)
    
    def draw_board(self):
        self.screen.fill((139, 69, 19))  # Brown background
        
        # Draw stores
        for store, pos in self.store_positions.items():
            pygame.draw.rect(self.screen, (101, 67, 33),
                           (pos[0] - self.store_width//2,
                            pos[1] - self.store_height//2,
                            self.store_width,
                            self.store_height))
            text = self.font.render(str(self.game.state.board[store]), True, (255, 255, 255))
            self.screen.blit(text, (pos[0] - 10, pos[1] - 10))
        
        # Draw pits
        for pit, pos in self.pit_positions.items():
            pygame.draw.circle(self.screen, (101, 67, 33), pos, self.pit_radius)
            text = self.font.render(str(self.game.state.board[pit]), True, (255, 255, 255))
            self.screen.blit(text, (pos[0] - 10, pos[1] - 10))
        
        pygame.display.flip()
    
    def get_clicked_pit(self, pos):
        for pit, pit_pos in self.pit_positions.items():
            if ((pos[0] - pit_pos[0])**2 + (pos[1] - pit_pos[1])**2)**0.5 <= self.pit_radius:
                return pit
        return None
    
    def run(self):
        while self.running:
            self.draw_board()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pit = self.get_clicked_pit(event.pos)
                    if pit and pit in self.game.state.player1_pits:
                        if self.game.state.doMove("player1", pit):
                            # Computer's turn
                            if not self.game.gameOver():
                                _, best_pit = self.minimaxAlphaBetaPruning(
                                    deepcopy(self.game), 1, 5, -inf, inf)
                                if best_pit:
                                    self.game.state.doMove("player2", best_pit)
            
            if self.game.gameOver():
                winner, score = self.game.findWinner()
                print(f"Game Over! Winner: {winner} with score: {score}")
                self.running = False
        
        pygame.quit()
    
    def minimaxAlphaBetaPruning(self, game, player, depth, alpha, beta):
        if game.gameOver() or depth == 0:
            return game.evaluate(), None
        
        if player == 1:  # MAX player (computer)
            best_value = -inf
            best_pit = None
            for pit in game.state.possibleMoves(game.playerSide[player]):
                child_game = deepcopy(game)
                child_game.state.doMove(game.playerSide[player], pit)
                value, _ = self.minimaxAlphaBetaPruning(child_game, -player, depth-1, alpha, beta)
                if value > best_value:
                    best_value = value
                    best_pit = pit
                alpha = max(alpha, best_value)
                if beta <= alpha:
                    break
            return best_value, best_pit
        else:  # MIN player (human)
            best_value = inf
            best_pit = None
            for pit in game.state.possibleMoves(game.playerSide[player]):
                child_game = deepcopy(game)
                child_game.state.doMove(game.playerSide[player], pit)
                value, _ = self.minimaxAlphaBetaPruning(child_game, -player, depth-1, alpha, beta)
                if value < best_value:
                    best_value = value
                    best_pit = pit
                beta = min(beta, best_value)
                if beta <= alpha:
                    break
            return best_value, best_pit

if __name__ == "__main__":
    gui = MancalaGUI()
    gui.run()
