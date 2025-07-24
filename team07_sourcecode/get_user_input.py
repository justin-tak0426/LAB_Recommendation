
# return user input from the console
def get_user_input():
    """
    Function to get user input from the console.
    
    Returns:
        str: The input provided by the user.
    """
    try:
        user_input = input("Please enter your input: ")
        return user_input
    except EOFError:
        print("Input was interrupted.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:
        print("Input process completed.")
