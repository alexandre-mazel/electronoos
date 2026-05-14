#@title 2025-02-20 - MASTERMIND avec Alex et Myriam

import itertools

# List of 8 possible colors.
colors = ['white', 'yellow', 'red', 'blue', 'green', 'violet', 'pink', 'orange']

def compute_feedback(guess, secret):
    """
    Compute the feedback for a guess against a secret.
    Returns a tuple (correct_position, correct_color_wrong_position)
    where:
      - correct_position corresponds to "OK" (right color, right position)
      - correct_color_wrong_position corresponds to "ok" (right color, wrong position)
    """
    # Count correct positions.
    correct_pos = sum(1 for i in range(4) if guess[i] == secret[i])

    # Build lists for colors not already matched exactly.
    guess_remaining = []
    secret_remaining = []
    for i in range(4):
        if guess[i] != secret[i]:
            guess_remaining.append(guess[i])
            secret_remaining.append(secret[i])

    # Count right colors in wrong positions.
    correct_color_wrong_pos = 0
    for color in set(guess_remaining):
        correct_color_wrong_pos += min(guess_remaining.count(color), secret_remaining.count(color))

    return (correct_pos, correct_color_wrong_pos)

def parse_feedback(feedback_str):
    """
    Parse feedback string from the user.
    "OK" means one correct and well placed.
    "ok" means one correct but wrong placed.
    The order does not matter.
    Returns a tuple (number_of_OK, number_of_ok).
    """
    tokens = feedback_str.strip().split()
    count_OK = sum(1 for token in tokens if token == "OK")
    count_ok = sum(1 for token in tokens if token == "ok")
    return (count_OK, count_ok)

def main():
    # Generate all possible 4-color combinations.
    possibilities = list(itertools.product(colors, repeat=4))

    # Initial guess: arbitrarily chosen.
    guess = ('white', 'yellow', 'red', 'blue')

    while True:
        print("Guess:", ' '.join(guess))
        feedback_str = input("Enter feedback (e.g., 'OK ok ok'): ").strip()
        feedback = parse_feedback(feedback_str)

        # If all 4 are correct and in the right position, the code is found.
        if feedback == (4, 0):
            print("Found the secret code!")
            break

        # Filter possibilities based on the feedback from the current guess.
        possibilities = [p for p in possibilities if compute_feedback(guess, p) == feedback]

        if not possibilities:
            print("No possibilities remain. Please check the feedback for consistency.")
            break

        # Next guess: choose the first possibility from the filtered list.
        guess = possibilities[0]

if __name__ == "__main__":
    main()