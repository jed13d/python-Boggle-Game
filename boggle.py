'''   boggle.py

      Justin Dowell
'''
# imports
#--------------------------------------------
from __future__ import print_function
from Tkinter import *

import copy, enchant, os, pickle, random, string, threading, time
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# initializations
#--------------------------------------------
is_word = enchant.Dict("en_US")
dice_array = [["A", "E", "A", "N", "E", "G"], ["A", "H", "S", "P", "C", "O"], ["A", "S", "P", "F", "F", "K"], ["O", "B", "J", "O", "A", "B"], ["I", "O", "T", "M", "U", "C"], ["R", "Y", "V", "D", "E", "L"], ["L", "R", "E", "I", "X", "D"], ["E", "I", "U", "N", "E", "S"], ["W", "N", "G", "E", "E", "H"], ["L", "N", "H", "N", "R", "Z"], ["T", "S", "T", "I", "Y", "D"], ["O", "W", "T", "O", "A", "T"], ["E", "R", "T", "T", "Y", "L"], ["T", "O", "E", "S", "S", "I"], ["T", "E", "R", "W", "H", "V"], ["N", "U", "I", "H", "M", "Qu"]]
player_history_initial_text = "         Word History\n------------------------------\n"
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# some preloaded messages
#--------------------------------------------
STATUS_BAR_DICT = {
   "new_game_message":"Begin typing words below, <enter> to submit.",
   "repeated_word_error":"That word has already been used.",
   "word_too_short_error":"That word is too short.",
   "word_not_a_word_error":"That word is ... not a word.",
   "word_not_possible_error":"That word is not present.",
   "word_one_point":"1 point.",
   "word_two_point":"2 points.",
   "word_three_point":"3 points.",
   "word_five_point":"5 points!",
   "word_eleven_point":"11 points!"
      }
STATUS_SUCCESS = {
   "word_one_point":1,
   "word_two_point":2,
   "word_three_point":3,
   "word_five_point":5,
   "word_eleven_point":11
      }
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Boggle_Game_Class
#--------------------------------------------
class Boggle_Game_Class:
   # __init__()
   #-----------------------------------------
   def __init__( self, master ):
      self.player_score = 0
      self.master = master
      self.first_start_alert = None
      self.load_alert = None
      self.time_over_alert = None
      self.file_to_load = ""
      # game_state is used for saving and loading games
      self.game_state = {}
      # menu bar initialization
      self.menu_bar = Menu( self.master )
      self.game_menu = Menu( self.menu_bar, tearoff=0 )
      self.game_menu.add_command( label="New", command=self.new_game )
      self.game_menu.add_separator()
      self.game_menu.add_command( label="Save", command=self.save_game )
      self.game_menu.add_command( label="Load", command=self.load_window )
      self.game_menu.add_separator()
      self.game_menu.add_command( label="Quit", command=self.end_game )
      self.menu_bar.add_cascade( label="Game", menu=self.game_menu )
      self.master.config( menu=self.menu_bar )
      # game tray initialization
      self.game_tray = Game_Tray_Class( self.master )
      # history display box
      self.player_history = Word_History_Class( self.master )
      # entry status bar
      self.status_bar = Status_Bar_Class( self.master )
      # player entry box
      self.player_entry_string = StringVar()
      self.player_entry = Entry( self.master, textvariable=self.player_entry_string, width=40, font=( "Courier", 14 ) )
      self.player_entry.grid( row=5, column=0, columnspan=6, sticky=W )
      self.player_entry.bind( "<Return>", self.process_entry )
      # timer and timer box
      self.init_timer()
      # startup popup
      self.first_start()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # close_all_popups
   #-----------------------------------------
   def close_all_popups( self ):
      if self.first_start_alert is not None:
         self.first_start_alert.destroy()
         self.first_start_alert = None
      if self.load_alert is not None:
         self.load_alert.destroy()
         self.load_alert = None
      if self.time_over_alert is not None:
         self.time_over_alert.destroy()
         self.time_over_alert = None
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # end_game
   #-----------------------------------------
   def end_game( self ):
      self.time_pause()
      self.master.quit()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # first_start
   #-----------------------------------------
   def first_start( self ):
      self.first_start_alert = Toplevel()
      self.first_start_alert.attributes( "-topmost", True )
      self.first_start_alert.geometry( "243x50+350+250" )
      self.first_start_alert.title(" Welcome! ")
      # message
      message = Label( self.first_start_alert, text=" Please select an option: " )
      message.grid( row=0, column=0, columnspan=2 )
      # buttons
      button1 = Button( self.first_start_alert, text=" Start New Game ", command=self.new_game )
      button1.grid( row=1, column=0 )
      button2 = Button( self.first_start_alert, text=" Load Game ", command=self.load_window )
      button2.grid( row=1, column=1 )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # init_timer
   #-----------------------------------------
   def init_timer( self ):
      self.timer_seconds = 180
      self.timer_string = StringVar()
      self.timer_string.set( str( self.timer_seconds / 60 ) + ":" + str( self.timer_seconds % 60 ) )
      self.timer_label = Label( self.master, textvariable=self.timer_string, width=10, font=( "Courier", 14, "bold" ) )
      self.timer_label.grid( row=5, column=6 )
      self.timer = threading.Timer( 1.0, self.time_update )
      self.timer.start()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # load_window
   #-----------------------------------------
   def load_window( self ):
      # initialization
      files_found = []
      self.load_alert = Toplevel()
      self.load_alert.geometry( "215x200+625+250" )
      self.load_alert.attributes( "-topmost", True )
      self.load_alert.title("Load Game")
      message = Label( self.load_alert, text="Select a game to load:" )
      message.pack()
      self.filename_display = Listbox( self.load_alert, selectmode=SINGLE )
      # get file names
      file_list = os.listdir( "." )
      for each in file_list:
         if each.endswith( ".p" ):
            files_found.append( each )
      files_found.sort()
      files_found.reverse()
      for each in files_found:
         self.filename_display.insert( END, each )
      self.filename_display.bind( "<Double-Button-1>", self.load_game_event )
      self.filename_display.pack()
      load_button = Button( self.load_alert, text=" Load ", command=self.load_game )
      load_button.pack()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # load_game_event
   #-----------------------------------------
   def load_game_event( self, event ):
      self.load_game()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # load_game
   #-----------------------------------------
   def load_game( self ):
      # stop timer thread and load state
      self.time_pause()
      self.game_state = pickle.load( open( self.filename_display.get( self.filename_display.curselection()[0] ), "rb" ) )
      # player entry box
      self.player_entry_string.set( "" )
      self.player_entry.focus_force()
      # dice restoration
      self.game_tray.tray_list = self.game_state[ "tray" ]
      self.game_tray.restore_tray()
      # word history restoration
      self.player_history = Word_History_Class( self.master )
      self.game_tray.used_word_list = self.game_state[ "history" ]
      self.player_history.restore_history_box( self.game_state[ "history" ] )
      # destroy alert box
      self.close_all_popups()
      # timer restoration
      self.timer_seconds = self.game_state[ "time" ]
      self.timer_string.set( str( self.timer_seconds / 60 ) + ":" + str( self.timer_seconds % 60 ) )
      self.timer = threading.Timer( 1.0, self.time_update )
      self.timer.start()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # new_game_event
   #-----------------------------------------
   def new_game_event( self, event ):
      self.new_game()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # new_game
   #-----------------------------------------
   def new_game( self ):
      self.time_pause()
      # player entry box
      self.player_entry_string.set( "" )
      self.player_entry.focus_force()
      # game tray shuffle
      self.game_tray.shuffle()
      # history display box
      self.player_history = Word_History_Class( self.master )
      # status bar
      self.status_bar.status_message.set( STATUS_BAR_DICT['new_game_message'] )
      # timer and timer box
      self.init_timer()
      # destroy alert box
      self.close_all_popups()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # process_entry
   #-----------------------------------------
   def process_entry( self, event ):
      status_message_string = self.game_tray.check_word( self.player_entry_string.get() )
      self.status_bar.status_message.set( STATUS_BAR_DICT[status_message_string] )
      if status_message_string in STATUS_SUCCESS:
         self.player_history.add_word( self.player_entry_string.get() )
         self.player_score += STATUS_SUCCESS[status_message_string]
      self.player_entry_string.set( "" )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # save_game
   #     1. Saving and restoring the dice configuration.
   #     2. Saving and restoring the words already entered (i.e. the ones in the right text box).
   #     3. Saving and restoring the time left on the clock.
   #-----------------------------------------
   def save_game( self ):
      # save state
      self.game_state[ "tray" ] = self.game_tray.tray_list
      self.game_state[ "history" ] = self.game_tray.used_word_list
      self.game_state[ "time" ] = self.timer_seconds
      # store date_time into time_stamp
      time_stamp = time.asctime( time.localtime( time.time() ) ) + ".p"
      # save state to file
      pickle.dump( self.game_state, open( time_stamp, "wb" ) )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # time_pause
   #-----------------------------------------
   def time_pause( self ):
      self.timer.cancel()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # time_over
   #-----------------------------------------
   def time_over( self ):
      self.time_over_alert = Toplevel()
      self.time_over_alert.geometry( "210x60+350+250" )
      self.time_over_alert.attributes( "-topmost", True )
      self.time_over_alert.title("Time\'s Up!")
      # message
      time_over_message = " Time\'s up! You scored " + str( self.player_score ) + " points!\n Would you like to play again?"
      message = Label( self.time_over_alert, text=time_over_message )
      message.grid( row=0, column=0, columnspan=2 )
      # buttons
      button1 = Button( self.time_over_alert, text=" Yes ", command=self.new_game )
      button1.grid( row=1, column=0 )
      button2 = Button( self.time_over_alert, text=" No ", command=self.end_game )
      button2.grid( row=1, column=1 )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # time_update
   #-----------------------------------------
   def time_update( self ):
      self.timer_seconds -= 1
      self.timer_string.set( str( self.timer_seconds / 60 ) + ":" + str( self.timer_seconds % 60 ) )
      if( self.timer_seconds == 0 ):
         self.time_over()
      else:
         self.timer = threading.Timer( 1.0, self.time_update )
         self.timer.start()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Game_Tray_Class class
#  -  builds dice tray
#  -  checks words for legality within rules and dice tray
#--------------------------------------------
class Game_Tray_Class:
   # __init__()
   #-----------------------------------------
   def __init__( self, master ):
      self.tray_frame = Frame( master ).grid( row=0, column=0 )
      self.shuffle()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # check_word()
   #  -  returns key from STATUS_BAR_DICT for further processing
   #  -  if word checks out, finish processing
   #-----------------------------------------
   def check_word( self, word ):
      char_list = list( word.upper() )   # make str to list and cleanup "Qu"
      for c in char_list:
         if c == 'Q':
            char_list[char_list.index( c )] = 'Qu'
            char_list.remove( 'U' )
      present_one = 1
      present_two = 1
      if word in self.used_word_list:    # word already scored
         return "repeated_word_error"
      if len( word ) < 3:                # word too short
         return "word_too_short_error"
      if not is_word.check( word ):      # dictionary check
         return "word_not_a_word_error"
      for n in char_list:           # check letters in word available on tray
         for i in self._tray:
            if n in i:
               break
         else:
            present_one = 0
      if not self.match_found( char_list, [] ):   # check possible path
         present_two = 0
      if not present_one or not present_two:
         return "word_not_possible_error"  # word not possible
      # word checks out - store and return message
      if present_one and present_two:
         self.used_word_list.append( word )
         if len( word ) < 5:
            return "word_one_point"
         elif len( word ) == 5:
            return "word_two_point"
         elif len( word ) == 6:
            return "word_three_point"
         elif len( word ) == 7:
            return "word_five_point"
         else:
            return "word_eleven_point"
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # draw_tray()
   #  -  uses self.tray_list to generate gui_tray
   #-----------------------------------------
   def draw_tray( self ):
      # value used to iterate through self.tray_list
      i = 0
      # generate and place gui 'dice'
      for y in xrange( 0, 4 ):
         for x in xrange( 0, 4 ):
            Label( self.tray_frame, text=self.tray_list[i], bg="black", fg="green", relief=RAISED, width=2, height=1, font=( "Courier", 42, "bold" ) ).grid( row=y, column=x )
            i += 1
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # is_adjacent()
   #    this function returns true if the given coordinates are adjacent, false otherwise
   #  * note - this doesn't check for repeated visits because it's done before calling this
   #-----------------------------------------
   def is_adjacent( self, here, last ):
      allowed = [-1, 0, 1]
      if (here[0] - last[0]) in allowed and (here[1] - last[1]) in allowed:
         return 1
      else:
         return 0
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # match_found()
   #    this function is a recursive function attempting to find a successful path
   #        within the tray with the given word,
   #    word is a list of characters for comparing against dice
   #    visit_hist is expecting an empty list at start, is list of used coordinates
   #-----------------------------------------
   def match_found( self, word, visit_hist=[] ):
      if word == []:
         return 1
      for y in xrange(0, 4):
         for x in xrange(0, 4):
            if word[0] == self._tray[y][x] and not [y, x] in visit_hist:
               if visit_hist == [] or self.is_adjacent([y, x], visit_hist[-1]):
                  visit_hist.append([y, x])
                  if self.match_found( word[1:], visit_hist ):
                     return 1
                  else:
                     visit_hist.pop()
                     continue
               else:
                  continue
      else:
         return 0
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # restore_tray()
   #     simply fills self._tray, used for word matching
   #-----------------------------------------
   def restore_tray( self ):
      self._tray = [ self.tray_list[:4], self.tray_list[4:8], self.tray_list[8:12], self.tray_list[12:] ]
      self.draw_tray()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # shuffle()
   #  -   shuffles the tray
   #  -   self.tray_list - used for drawing
   #-----------------------------------------
   def shuffle( self ):
      # clear history
      self.used_word_list = []
      # make sure tray is empty
      self.tray_list = []
      for i in xrange( 0, 16 ):
         # 'roll' the dice and store the result
         self.tray_list.append( random.choice( dice_array[i] ) )
      # shuffle position of each die
      random.shuffle( self.tray_list )
      # place dice in tray
      self.restore_tray()
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Status_Bar_Class
#  -  manages the status bar and output
#--------------------------------------------
class Status_Bar_Class:
   # __init__()
   #-----------------------------------------
   def __init__( self, master ):
      self.status_message = StringVar()
      self.status_message.set( STATUS_BAR_DICT['new_game_message'] )
      self.status_bar = Label( master, textvariable=self.status_message, width=50, justify=LEFT, font=( "Courier", 14, "bold" ) ).grid( row=4, column=0, columnspan=7, sticky=W )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # display_message()
   #-----------------------------------------
   def display_message( self, message ):
      self.status_message.set( STATUS_BAR_DICT['new_game_message'] )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# Word_History_Class
#  -  builds dice tray
#  -  checks words for legality within rules and dice tray
#--------------------------------------------
class Word_History_Class:
   # __init__()
   #-----------------------------------------
   def __init__( self, master ):
      self.player_word_history = []
      self.player_history_box = Text( master, width=30, height=14, font=( "Courier", 12 ) )
      self.player_history_box.grid( row=0, column=5, rowspan=4, columnspan=2 )
      self.player_history_box.insert( INSERT, player_history_initial_text )
      self.player_history_box.config( state=DISABLED )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # add_word()
   #  -  adds a single word to the player history display box
   #  -  adds word to word history list for state saving
   #-----------------------------------------
   def add_word( self, word ):
      temp = word + "\n"
      self.player_word_history.append( word )
      self.player_history_box.config( state=NORMAL )
      self.player_history_box.insert( INSERT, temp )
      self.player_history_box.config( state=DISABLED )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

   # restore_history_box()
   #  -  restores saved state from list of words
   #  -  adds word to word history list for state saving
   #-----------------------------------------
   def restore_history_box( self, word_list ):
      for word in word_list:
         self.add_word( word )
   #+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# main()
#--------------------------------------------
def main():
   # root screen
   root = Tk()
   root.geometry( "594x333+300+200" )
   root.title( "Boggle.py" )
   game = Boggle_Game_Class( root )
   # start gui loop
   root.mainloop()
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

if __name__ == "__main__": main()