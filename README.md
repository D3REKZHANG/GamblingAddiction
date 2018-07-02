# GamblingAddiction
Discord bot written in Python 3 to play Texas Holdem.  

Created using Discord.py and Deuces, a poker hand evaluation library I found on Github (https://github.com/worldveil/deuces). 

<h2>Implementation Notes</h2>
The bot utilises many of the tools Discord.py offers, and the code is structured around the API. There are classes for players, cards, 
and games for easier coding. Player data is stored in once massive json which is opened and edited with every command that requires it.
This is not very optimized but it is fast enough since most Discord servers have less than 100000 members. 
<p></p>
All code was written in Python 3.6, and I edited Deuces code to make it Python 3 friendly (quite the headache). The IDE that I used was 
Sublime Text 3, and a simple batch file is used to start up the bot. The client token is in a file I keep locally and is referenced in the 
driver to run the bot. 

<h2>Features</h2>
The bot can simulate an accurate game of Texas Holdem, and uses a local currency stored in the data.json file. Cards are represented with 
text (2-10,J,Q,K,A) and a discord suit emoji (:diamonds:, :hearts:, :diamonds:, :clubs:). All interactions happen in the server channel that the game was 
started in. Each player's hand is direct messaged to the user, and is given updates on the table cards as well as their current best 
hand each round.

<p></p>

The bot can run multiple games in different channels and supports up to 8 players per game (this is a coded value). Players can give and
receive money from eachother and everyone can beg the bot for $10 once daily. All commands are error trapped, with good error messages. It
is impossible to break or crash the bot. 
