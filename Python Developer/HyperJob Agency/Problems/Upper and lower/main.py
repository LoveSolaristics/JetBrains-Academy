# the list with words from string
# please, do not modify it
some_iterable = input().split()

# use dictionary comprehension to create a new dictionary
print({elem.upper(): elem.lower() for elem in some_iterable})