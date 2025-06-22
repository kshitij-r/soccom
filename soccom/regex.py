import re

# .       - Any Character Except New Line
# \d      - Digit (0-9)
# \D      - Not a Digit (0-9)
# \w      - Word Character (a-z, A-Z, 0-9, _)
# \W      - Not a Word Character
# \s      - Whitespace (space, tab, newline)
# \S      - Not Whitespace (space, tab, newline)

# \b      - Word Boundary
# \B      - Not a Word Boundary
# ^       - Beginning of a String
# $       - End of a String

# []      - Matches Characters in brackets
# [^ ]    - Matches Characters NOT in brackets
# |       - Either Or
# ( )     - Group

# Quantifiers:
# *       - 0 or More
# +       - 1 or More
# ?       - 0 or One
# {3}     - Exact Number
# {3,4}   - Range of Numbers (Minimum, Maximum)

text_to_search = '''
abc1234567890
ABCqwertyuiop
abcdefgh
Kshitij
intel
apple
qualcomm
samsung
apple.com
Ha HaHa
321-555-4321
123.555.1234
123*555*1234
800-555-1234
900-555-1234
Mr. Schafer
Mr Smith
Ms Davis
Mrs Robinson
Mr. T
Meta Characters that need to be escaped: 
 . ^ $ * + ? { } [ ] \ | ( )
'''

sentence='This is a raw string'

emails='''
CoreyMschafer@gmail.com
corey.schafer@university.edu
corey-321-schafer@my-work.net
'''

urls='''
https://www.google.com
http://coreyms.com
https://www.youtube.com
https://www.nasa.gov
'''
#pattern=re.compile(r'[97]00[.-]\d\d\d[.-]\d\d\d\d')
#pattern=re.compile(r'Mr\.') This matches strings with Mr.
#pattern=re.compile(r'Mr\.?') This matches strings with Mr or Mr. (. is optional)
#pattern=re.compile(r'Mr\.?\s')  This matches strings with Mr or Mr. (. is optional) and the whitespace(\s) after .
#pattern=re.compile(r'Mr\.?\s[A-Z]')This matches strings with Mr or Mr. (. is optional) and the whitespace(\s) after . and all upper case letters after whitespace
pattern=re.compile(r'M(r|s|rs)\.?\s[A-Z]\w*')

mail_pattern= re.compile(r'[a-zA-Z0-9.-]+@[a-zA-Z-]+\.(com|edu|net)')

site_pattern=re.compile(r'https?://(www\.)?(\w+)(\.\w+)')

matches=site_pattern.finditer(urls)

with open('data.txt','r') as f:
   contents=f.read()
   #matches=pattern.finditer(contents)

for match in matches:
   print(match.group(3))

subs_url = site_pattern.sub(r'\2\3',urls)
print(subs_url)

case= 'This is to test case insensitivity of re module'

check_case= re.compile(r'this', re.IGNORECASE)
to_print=check_case.search(case)
print(to_print)
