# MTGHandAnalyzer
This program is designed to help Magic: The Gathering players gain insights about the decks that they play in order to up their game. A player can record their opening hands and a few other details (such as whether or not they won that game, whether it was game 1/2/3, the deck their opponent was playing, etc.). Then the program will spit out some analysis of the matches to try and give some actionable advice.

Currently, MTGHandAnalyzer can supply the following information:
- Game win %
- Total games played
- Most common cards to see in any given hand
- The win % of opening hands with a given card in it
- The number of times you mulliganed and your win % by the number of mulligans taken
- A prediction for your chances of winning, based on a given opening hand

In the future, I plan to add:
- Win % in game 1 vs. sideboarded games
- Statistics for matchups against opponent's archetypes
- Functionality to have the program be able to make mulligan decisions on its own, given the cards drawn and some parameters about the game situation.
- Better training for predictions and picking a method of analysis that produces the most accurate results
