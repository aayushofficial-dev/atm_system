# Write a python program to find the number is even or odd.

# num = int(input("Enter a number:"))

# if num % 2 == 0:
#     print(f"{num} is an even number.")
# else:
#     print(f"{num} is an odd number.")

# Write a python program to find the largest of three numbers.

# num1 = float(input("Enter first number:"))
# num2 = float(input("Enter second number:"))
# num3 = float(input("Enter third number:"))

# if num1 >= num2 and num1 >= num3:
#     largest = num1
# elif num2 >= num1 and num2 >= num3:
#     largest = num2
# else:
#     largest = num3 

# print(f"The largest number is: {largest}")

# Write a python program to check if a number is prime or not.

number = int(input("Enter a number:"))

if number > 1:
    for i in range(2, int(number**0.5) + 1):
        if number % i == 0:
            print(f"{number} is not a prime number.")
            break
        else:
            print(f"{number} is a prime number.")
            break
    else:
        print(f"{number} is a prime number.")