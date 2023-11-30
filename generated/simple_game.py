import random

number = random.randint(1, 10)

print('Welcome to Guess the Number!')
print('The rules are simple. I will think of a number between 1 and 10, and you have to guess it.')

guess = int(input('Enter your guess: '))

if guess == number:
    print('Congratulations! You guessed the number.')
else:
    print('Sorry, better luck next time. The number was', number) 