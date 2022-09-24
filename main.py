import tkinter as tk
import random
import numpy as np
from itertools import product
import time
from math import floor


def main():
    program = WordGame()
    program.root.mainloop()


class WordGame:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('300x400')
        self.root.resizable(False, False)
        self.root.title('Sanapeli')
        self.frame = tk.Frame(self.root)
        self.frame.pack()

        self.tic = time.perf_counter()
        self.rows = 10
        self.cols = 10
        self.buttons = [[None] * self.cols for _ in range(self.rows)]
        self.button_texts = np.zeros((self.rows, self.cols), dtype=object)
        self.chosen_buttons = []
        self.submitted_buttons = np.zeros((self.rows, self.cols))
        self.word_message = None
        self.submit_button = None
        self.delete_button = None
        self.new_game_button = None
        self.word = ''
        self.tries = 0
        self.word_to_be_deleted = 0
        self.tiling = None

        self.create_widgets()

    def create_widgets(self):

        self.init_letters()
        print('Tries: ', self.tries)
        self.word_message = tk.Message(self.frame, text='Valitse kirjaimia', width=200)
        self.word_message.grid(row=self.rows + 1, columnspan=self.cols)

        self.submit_button = tk.Button(self.frame, text='Ei ole hyväksytty sana', state='disabled',
                                       command=self.submit_word)
        self.submit_button.grid(row=self.rows + 2, columnspan=self.cols)

        self.delete_button = tk.Button(self.frame, text='Poista tämä sana', state='disabled', command=self.delete_word)
        self.delete_button.grid(row=self.rows + 3, columnspan=self.cols)

        self.new_game_button = tk.Button(self.frame, text='Näytä ratkaisu', command=self.print_solution)
        self.new_game_button.grid(row=self.rows + 4, columnspan=self.cols)

        self.new_game_button = tk.Button(self.frame, text='Uusi peli', command=self.refresh)
        self.new_game_button.grid(row=self.rows + 5, columnspan=self.cols)

    def create_seeds(self, no_of_submitted_words):
        tiles = np.zeros((self.rows, self.cols))
        coords = random.sample(list(product(range(10), repeat=2)), k=no_of_submitted_words)
        # Create the seeds for different tiles
        for i in range(no_of_submitted_words):
            tiles[coords[i][0], coords[i][1]] = i+1
        return tiles, coords

    def init_letters(self):
        self.tries = self.tries + 1
        no_of_submitted_words = np.random.randint(15, 18)
        tiles, coords = self.create_seeds(no_of_submitted_words)
        # Idea is to randomly select squares not in tiles yet and add them to neighbouring tiles until the whole
        # rectangle is filled
        n = 0
        while np.count_nonzero(tiles == 0) > 0:
            n = n+1
            if n == 200:
                self.init_letters()
                return
            apu = np.where(tiles == 0)
            rand_index = random.sample(range(len(apu[0])), 1)
            coord = (apu[0][rand_index][0], apu[1][rand_index][0])
            neighbours = []
            total_neighbours = 0
            # Draw random points and join them to some neighbouring tile
            if coord[0] < self.rows-1:  # Have not checked if this works when rows != cols or if it's wrong way around
                total_neighbours = total_neighbours + 1
                if tiles[coord[0]+1][coord[1]] != 0:
                    neighbours.append(tiles[coord[0]+1][coord[1]])
            if coord[0] > 0:
                total_neighbours = total_neighbours + 1
                if tiles[coord[0]-1][coord[1]] != 0:
                    neighbours.append(tiles[coord[0]-1][coord[1]])
            if coord[1] < self.cols-1:
                total_neighbours = total_neighbours + 1
                if tiles[coord[0]][coord[1]+1] != 0:
                    neighbours.append(tiles[coord[0]][coord[1]+1])
            if coord[1] > 0:
                total_neighbours = total_neighbours + 1
                if tiles[coord[0]][coord[1]-1] != 0:
                    neighbours.append(tiles[coord[0]][coord[1]-1])
            if neighbours:
                areas = []
                for k in range(len(neighbours)):
                    areas.append(np.count_nonzero(tiles == neighbours[k]))
                # Preferably fill areas that are smaller than 4
                if sum(i < 4 for i in areas) > 0:
                    indices = [j for j, v in enumerate(areas) if v < 4]
                    chosen_index = random.sample(indices, 1)
                    coord_tile = neighbours[chosen_index[0]]
                # If all neighbours are length 8, tiling is not acceptable, and we try again
                elif sum(i == 8 for i in areas) == total_neighbours:
                    # raise Exception("All neighbours are length 8!")
                    self.init_letters()
                    return
                else:
                    indices = [j for j, v in enumerate(areas) if v < 8]
                    if not indices:
                        continue
                    chosen_index = random.sample(indices, 1)
                    coord_tile = neighbours[chosen_index[0]]
                tiles[coord[0]][coord[1]] = coord_tile

        # print('Tiles before expanding:\n', tiles)

        # If some tile is smaller than 4, we try to give it extra squares from neighbours
        for i in range(1, no_of_submitted_words+1):
            elements_count = np.count_nonzero(tiles == i)
            if elements_count < 4:
                for j in range(4 - elements_count):
                    tiles = self.expand_tile(tiles, i)
                    if not tiles.any():
                        self.init_letters()
                        return

        # print('Tiles after expanding:\n', tiles)
        # Add letters to buttons
        self.tiling = tiles
        self.add_words(tiles)
        for row in range(self.rows):
            for col in range(self.cols):
                self.buttons[row][col] = tk.Button(self.frame, text=self.button_texts[row][col],
                                                   command=lambda r=row, c=col: self.click_letter(r, c))
                self.buttons[row][col].grid(row=row, column=col, sticky="nsew")

    def add_words(self, tiles):
        for i in range(1, int(np.amax(tiles))+1):
            no_of_letters = np.count_nonzero(tiles == i)
            file = f'kotus_sanalista_{no_of_letters}.txt'
            chosen_word = random.choice(open(file).readlines())
            chosen_word = chosen_word[:-1]
            chosen_word = chosen_word.replace("Ã¶", 'ö')
            chosen_word = chosen_word.replace("Ã¤", 'ä')
            where = np.where(tiles == i)
            for j in range(len(chosen_word)):
                self.button_texts[where[0][j]][where[1][j]] = chosen_word[j]

    def expand_tile(self, tiles, i):
        nonzero = np.nonzero(tiles == i)
        neighbours = []
        small_tile = []
        for j in range(len(nonzero[0])):
            small_tile.append([nonzero[0][j], nonzero[1][j]])
        for letr in small_tile:
            if letr[0] < self.rows - 1 and tiles[letr[0] + 1][letr[1]] != i:
                neighbours.append([letr[0] + 1, letr[1]])
            if letr[0] > 0 and tiles[letr[0] - 1][letr[1]] != i:
                neighbours.append([letr[0] - 1, letr[1]])
            if letr[1] < self.cols - 1 and tiles[letr[0]][letr[1] + 1] != i:
                neighbours.append([letr[0], letr[1] + 1])
            if letr[1] > 0 and tiles[letr[0]][letr[1] - 1] != i:
                neighbours.append([letr[0], letr[1] - 1])
        random.shuffle(neighbours)
        for candidate in neighbours:
            tiles_new = tiles.copy()
            tiles_new[candidate[0]][candidate[1]] = i
            old_tile = tiles[candidate[0]][candidate[1]]

            where = np.where(tiles_new == old_tile)
            consumed_tile_list = []
            for j in range(len(where[0])):
                consumed_tile_list.append([where[0][j], where[1][j]])
            if len(np.where(tiles == old_tile)[0]) >= 5 and self.check_if_contiguous(consumed_tile_list):
                return tiles_new
        # raise Exception("Could not expand tile")
        # If we get here, we could not expand tile. Let's try again.
        return np.zeros(1)

    def click_letter(self, r, c):

        if self.submitted_buttons[r][c]:
            if len(self.chosen_buttons) == 0:
                self.delete_button.config(state='active')
                self.word_to_be_deleted = self.submitted_buttons[r][c]
            return

        self.delete_button.config(state='disabled')
        clicked_btn = self.buttons[r][c]
        if clicked_btn['bg'] == 'SystemButtonFace':
            new_color = 'blue'
            self.chosen_buttons.append([r, c])
        else:
            new_color = 'SystemButtonFace'
            self.chosen_buttons.remove([r, c])
        clicked_btn.config(bg=new_color)
        self.chosen_buttons.sort()

        is_one_area = self.check_if_contiguous(self.chosen_buttons)
        self.submit_button.config(state='disabled')
        self.submit_button.config(text='Ei ole hyväksytty sana')
        if not is_one_area:
            self.word_message.configure(text='Alueen täytyy olla yhtenäinen!')
        elif not self.chosen_buttons:
            self.word_message.configure(text='Valitse kirjaimia')
        elif len(self.chosen_buttons) <= 3:
            self.word = ''
            for coord in self.chosen_buttons:
                self.word = self.word + self.button_texts[coord[0]][coord[1]]  # self.button_texts[10 * coord[0] + coord[1]]
            self.word_message.configure(text=f'Liian lyhyt sana: {self.word}')
        elif len(self.chosen_buttons) > 8:
            self.word_message.configure(text='Liian pitkä sana')
        else:
            self.word = ''
            for coord in self.chosen_buttons:
                self.word = self.word + self.button_texts[coord[0]][coord[1]]  # Same as above
            self.word_message.configure(text=self.word)
            chosen_word = self.word.replace('ö', "Ã¶")
            chosen_word = chosen_word.replace('ä', "Ã¤")
            file = open(f'kotus_sanalista_{len(self.chosen_buttons)}.txt', 'r')
            if chosen_word in file.read():
                self.submit_button.config(state='active')
                self.submit_button.config(text='Valitse sana')

    def check_if_contiguous(self, squares):
        if not squares:  # squares.any()
            return True
        squares_copy = squares.copy()
        q = [squares[0]]
        connected_squares = set()

        while q:
            coord = q[0]
            q.remove(coord)
            if coord in squares_copy:
                squares_copy.remove(coord)
            connected_squares.add(tuple(coord))
            if [coord[0] + 1, coord[1]] in squares_copy:
                q.append([coord[0] + 1, coord[1]])
            if [coord[0] - 1, coord[1]] in squares_copy:
                q.append([coord[0] - 1, coord[1]])
            if [coord[0], coord[1] + 1] in squares_copy:
                q.append([coord[0], coord[1] + 1])
            if [coord[0], coord[1] - 1] in squares_copy:
                q.append([coord[0], coord[1] - 1])
        if len(connected_squares) == len(squares):
            return True
        else:
            return False

    def submit_word(self):
        colors = ['#e62f07', '#f3ef0d', '#1ff30d', '#0ee4ee', '#ee0ee7', '#116b34', '#d68b11',
                  '#5cedc9', '#6d6e6d', '#fa9a98', '#eafa98', '#7700a6', '#7d4845', '#d9c393',
                  '#a4a9eb', '#1ebd53', '#960f72', '#bfbfbf']
        no_of_new_word = 0
        while True:
            no_of_new_word = no_of_new_word + 1
            if no_of_new_word not in self.submitted_buttons:
                break
        for letter in self.chosen_buttons:
            button = self.buttons[letter[0]][letter[1]]
            button.config(bg=colors[(no_of_new_word-1) % len(colors)])
            self.submitted_buttons[letter[0]][letter[1]] = no_of_new_word
        self.word = ''
        self.word_message.configure(text=self.word)
        self.chosen_buttons = []

        # Check if game is finished
        if 0 not in self.submitted_buttons:
            toc = time.perf_counter()
            elapsed_time = toc - self.tic
            minutes = floor(elapsed_time/60)
            seconds = round(elapsed_time - minutes*60)
            win_popup = tk.Toplevel(self.root)
            win_popup.geometry("200x200")
            tk.Label(win_popup, text=f"Voitit!\nAika: {minutes} min {seconds} s.",
                     font='Helvetica 14 bold').pack(pady=20)
            win_popup.mainloop()

    def delete_word(self):
        freed_letters = np.argwhere(self.submitted_buttons == self.word_to_be_deleted)
        for i in range(len(freed_letters)):
            coord = freed_letters[i]
            self.submitted_buttons[coord[0]][coord[1]] = 0
            button = self.buttons[coord[0]][coord[1]]
            button.config(bg='SystemButtonFace')

    def refresh(self):
        self.root.destroy()
        self.__init__()

    def print_solution(self):
        print(self.tiling)


if __name__ == "__main__":
    main()
