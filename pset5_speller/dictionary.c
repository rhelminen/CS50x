// Implements a dictionary's functionality

#include <stdbool.h>
#include <string.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH + 1];
    struct node *next;
}
node;

// Number of buckets in hash table
const unsigned int N = 40000;

// Hash table
node *table[N];

// Counter for words added from the dictionary
int word_count = 0;

// Custom function to split words into 5 different categories
int calc_category(const char *word)
{
    if (strlen(word) < 4)
    {
        return 1;
    }

    if (word[1] > word[2])
    {
        if (word[3] % 2 == 0)
        {
            return 1;
        }
        else
        {
            return 2;
        }
    }

    else
    {
        if (word[3] % 2 == 0)
        {
            return 3;
        }
        else
        {
            if (strlen(word) > 5 && word[4] > word[5])
            {
                return 4;
            }
            else
            {
                return 5;
            }
        }
    }
}

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    // Convert word to lowercase
    char lowercase[LENGTH + 1] = {0};

    for (int i = 0; word[i]; i++)
    {
        lowercase[i] = tolower(word[i]);
    }

    // Obtain hash value of lowercase word
    unsigned int hash_value = hash(lowercase);

    // Create cursor to search through hash table
    node *cursor = table[hash_value];

    // Search the hash table. If end of table is reached without a match, return false
    while (cursor != NULL)
    {
        if (strcmp(lowercase, cursor->word) == 0)
        {
            return true;
        }
        cursor = cursor->next;
    }

    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    // I decided to challenge myself and write my own hash function first to see how good I can make it without resorting to copying existing code, the inner workings of which I might not completely understand.
    // After of a lot of testing and optimization, I managed to come up with a couple of ways to return relatively uncorrelated and evenly distributed values from the same string.
    // Each of the calculations returns a value of less than 10, so by treating them as digits of a larger value, I was able to create a 5-digit hash code that avoids collisions quite nicely.
    // While I would always use the best function available in a "real world situation", I think it was a valuable and fun exercise to try and come up with my own function, however imperfect it may be.

    // Initialize variables for the digits of the hash value
    int hash1 = 0;
    int hash3 = 0;
    int hash2 = 0;
    int hash4 = 0;
    int hash5 = word[0] - 'a' + 1;

    // Get 1st digit of hash value based on string length and whether strlen is an odd or even number
    if (strlen(word) < 9 || strlen(word) == 13)
    {
        hash1 = (strlen(word) % 2 == 0) ? 0 : 1;
    }
    else
    {
        hash1 = (strlen(word) % 2 == 0) ? 2 : 3;
    }

    // Get second digit based on first letter of the word. A few popular letters are split into two categories to balance it out.
    // My categorization is mostly based on Peter Norvig's article on English letter frequency counts at https://norvig.com/mayzner.html
    // ... and a fair bit of trial and error of course!
    if ((word[0] == 't' && word[0] > word[1]) || word[0] == 'm')
    {
        hash2 = 0;
    }
    else if ((word[0] == 't' && word[1] >= word[0]) || word[0] == 'p' || (word [0] == 'o' && word[0] > word[1]))
    {
        hash2 = 1;
    }
    else if (word[0] == 's' || word[0] == 'y')
    {
        hash2 = 2;
    }
    else if (word[0] == 'a' || word[0] == 'w')
    {
        hash2 = 3;
    }
    else if (word[0] == 'c' || word[0] == 'e')
    {
        hash2 = 4;
    }
    else if ((word[0] == 'o' && word[1] >= word[0]) || word[0] == 'l' || word[0] == 'g')
    {
        hash2 = 5;
    }
    else if (word[0] == 'r' || word[0] == 'i')
    {
        hash2 = 6;
    }
    else if (word[0] == 'h' || word[0] == 'u' || word[0] == 'n')
    {
        hash2 = 7;
    }
    else if (word[0] == 'b' || word[0] == 'f')
    {
        hash2 = 8;
    }
    else // z, x, v, j, k, q and d
    {
        hash2 = 9;
    }

    // Functions for digits 3-5
    for (int i = 0; word[i]; i++)
    {
        // hash4 gets the sum of the numerical values of the letters - 'a' (excluding apostrophes)
        if (isalpha(word[i]))
        {
            hash4 += word[i] - 'a';
        }

        // hash3 multiplies the first two letters of the word together (a == 1 to avoid multiplying with 0), and then starts subtracting the rest of the letters from the result
        if (i == 1)
        {
            hash3 *= word[i] - 'a' + 1;
        }
        else if (i > 1)
        {
            hash3 -= word[i] - 'a' + 1;
        }
    }

    // The last digit of the sum of letters
    hash4 = hash4 % 10;

    // The result of hash3 is often negative, so abs() makes sure that it gets turned into a positive value. hash5 reuses the result of hash3 but attempts to return a very different value.
    hash5 = abs(hash3) / 2;

    // The last digit of abs() of hash3
    hash3 = abs(hash3) % 10;

    // hash5 is still closely related to hash3, so it gets further processed through the calc_category() function to return a final value of 0-9.
    int category = calc_category(word);

    if (hash5 % 2 == 0)
    {
        switch (category)
        {
            case 1 :
                hash5 = 0;
                break;
            case 2 :
                hash5 = 1;
                break;
            case 3 :
                hash5 = 2;
                break;
            case 4 :
                hash5 = 3;
                break;
            case 5 :
                hash5 = 4;
        }
    }
    else
    {
        switch (category)
        {
            case 1 :
                hash5 = 5;
                break;
            case 2 :
                hash5 = 6;
                break;
            case 3 :
                hash5 = 7;
                break;
            case 4 :
                hash5 = 8;
                break;
            case 5 :
                hash5 = 9;
        }
    }

    // Combine separate digits to form the final hash value
    return hash1 * 10000 + hash2 * 1000 + hash3 * 100 + hash4 * 10 + hash5;


    // // Of course my simple hash function is no match to actual hash functions, so after I was relatively happy with it, I wanted to see how much faster and cleaner a better hash function could be.
    // // I was able to get to quite close to the speed of the staff's implementation using the djb2 hash function and a hash table of size 56171 (a prime number that seemed to work well)
    // // djb2 appears to be a very well known hash function and it was referenced in multiple sources. This is where I got the actual code from: https://theartincode.stanis.me/008-djb2/

    // unsigned long djb2 = 5381;
    // int c;

    // // c is assigned to the current character of word (dereferenced with *). Memory location within word (array of chars) increments on each iteration and the loop stops when *word points to NULL.
    // while ((c = *word++))
    // {
    //     // djb2 << 5 + djb2 essentially means djb * 33. It is using bit shifting instead of multiplication to achieve the same result (<< 5 is * 32 and then adding the original value makes it * 33)
    //     djb2 = ((djb2 << 5) + djb2) + c;
    // }

    // return djb2 % N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    // Open dictionary file
    FILE *infile = fopen(dictionary, "r");
    if (infile == NULL)
    {
        return false;
    }

    // Create a buffer for reading the words in the dictionary
    char buffer[LENGTH + 1];

    while (fscanf(infile, "%s", buffer) != EOF)
    {
        // Read current word into a new memory location
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            return false;
        }
        strcpy(n->word, buffer);
        n->next = NULL;

        // Hash word and insert node into hash table at the obtained location
        int location = hash(n->word);
        word_count++;

        if (table[location] == NULL)
        {
            table[location] = n;
        }
        else
        {
            n->next = table[location];
            table[location] = n;
        }
    }

    fclose(infile);
    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    if (word_count > 0)
    {
        return word_count;
    }
    return 0;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    // Create cursor and and a helper variable "tmp" to search the hash table
    node *cursor = NULL;
    node *tmp = NULL;

    // Unload dictionary
    for (int i = 0; i < N; i++)
    {
        // Set cursor and tmp to table[i]
        cursor = table[i];
        tmp = table[i];

        // Loop over the linked list found at current node, freeing "tmp" on each iteration
        while (cursor != NULL)
        {
            cursor = cursor->next;
            free(tmp);
            tmp = cursor;
        }
        table[i] = NULL;
    }

    if (table[N - 1] == NULL)
    {
        return true;
    }
    return false;
}
