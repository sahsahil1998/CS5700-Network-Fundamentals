This project was sn introduction to network programming where I impemented a client program that communicates with a socket server. The program then will read through several complex math expressions given back by the server and if it passes all correctly, then a secret password will be recieved back.

Figuring out how parse through a massive expression was quite difficult and I spent a long time trying to figure out how to properly and accurately read through the whole thing and produce the correct result. Eventually, I came across a few short youtube video that explained how this algorithim called the shunting yard algorithim worked by using stacks to parse through the massive expression and I was finally able to understand how to solve the math portion of the program. The socket programming itself was difficult initially but I read an intro guide to network prgramming which really helped me to understand what all is needed in the program to run the socket connection properly.

To test the code I added several lines of print statement throughput the main and the functions to see what part of the program was working up until and whenever it hit a specific print statement I would know there is an error there if it did not go past that line. To test the evaluation of the result I input in manually a few long math expressions I found online that would help me test for corner cases as well. I kept trying until I was able to send a proper connection to the server and finally was able to see the BYE message through a print statement and then able to slice out the secret flag.




 