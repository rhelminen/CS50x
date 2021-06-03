# Problem Set 5 - Speller
### Languages: C

https://cs50.harvard.edu/x/2021/psets/5/speller/

This program checks a text document against a dictionary and calculates how many words in the text document weren't found in the dictionary. It also outputs the time that it took to check the file, and the goal was to make it as fast as possible while using a reasonable amount of disk space.

The main challenge here (at least for me) was writing a hash function that is fast and efficient, distributing the words as evenly as possible in the hash table. I spent a lot of time coming up with my own hash function and optimizing it, and I think it turned out pretty well!

Using a hash function off the internet was also allowed for the assignment, so after I was happy with my own function, I wanted to also test a "real" hash function, and quickly found the djb2 function, which was only a few lines of code and works very well. My own function couldn't beat it of course, but coming up with it was a fun, challenging and a great exercise! I output the results of both functions in the `hash_results` directory where you can see how they performed on the large dictionary.

`dictionary.c` is the only file with my own code, the other files were provided in the distribution code.

## HOW TO USE

1. Install required packages. Alternatively, you can run the program on the [CS50 IDE](https://ide.cs50.io) (log in with your github account and upload the files there).

1. After compiling the code for `speller.c`, run with:
    ```
    $ ./speller DICTIONARY TEXT
    ```
    where `DICTIONARY` is either the large or small dictionary in `dictionaries` and `TEXT` is any of the text files in `texts`.
