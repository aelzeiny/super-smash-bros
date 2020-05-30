### Super Smash Bros Machine Learning Project

*Goal*: To create a neural network powerful enough to monitor smash gameplay in real-time

*Steps*:
1. Solder PCB board that can relay PC controller commands to the Nintendo Switch (done)
2. Create a library of macros to record/playback switch controls (done)
3. Create easy-to-use training studio that will assist in recording training data (done)
4. Record training data for every move, every character, every skin, on every stage in the game (in-progress)
5. Train real-time object recognition neural network to identify characters
6. Create service using AWS Kinesis Video Streams to monitor twitch feeds. (No longer thinking about Kafka)

### Smash Bros Macros

*Goal*: To create an automated way to extract training data from super-smash bros.

*Credit*: Please checkout [MFosse's & Pharoon's Switch Relay](https://github.com/Phroon/switch-controller). I use this
board to forward commands from my PC to the Switch!


*Updates*:
* 2019-02-01: After many attempts, I finally learned how to relay information from PC to switch. This project is officially possible.
* 2019-06-05: I quit the project because I couldn't get playback to be perfectly deterministic. I can record
controller inputs, but they don't land on the same frames every time. It's definitely an FPS issue.
* 2020-05-20: I finally solved the recording & playback issue! After rewriting this entire script in C# I noticed there
was no improvements to the FPS. Then I profiled the python repo to find that reading from the PCB board takes an awful
amount of time. So I commented out the read... and it actually works the way you expect now. Wow... Step #2 is finally
done!!!
* 2020-05-25: Now I'm building the libraries I need to record the macros. The goal is to record a file for every move
for every character in the game, and playback every stage/skin alteration. This will create a really rich dataset! But
is also really tidious. I don't look forward to this part.
* 2020-05-30: Hey, training_webserver.py is done along with Step 3! Pretty much this thing is multi-threaded like crazy
to ensure there are no desyncs in button presses. There's a front-end that connects to a flask server, that has 2
parallel processes. The first one sends commands over to the Switch Relay. The second sends commands over to the webcam
recorder. At this point, I should probably start recording.