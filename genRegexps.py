# MongoDB Shell Code Student Answer Checker V0.1
# Copyright (C) 2014 Juliet Christopher <jcbc98@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    https://www.gnu.org/copyleft/gpl.txt

import re

# Function decorator to mimic static variable behavior
# Ref: http://stackoverflow.com/questions/279561/what-is-the-python-equivalent-of-static-variables-inside-a-function
def static_var(varname, value):
  def decorate(func):
      setattr(func, varname, value)
      return func
  return decorate

# Static variable to keep track of grouping markers in regular expressions
@static_var("counter", 1)
def marker(reset=False):
  if reset:
    marker.counter = 1
  else:
    marker.counter += 1

# Generates permutations of a list
def permutations(elts):
  """Assumes elts is a list
     Returns a list of lists with all orderings of elts."""
  if len(elts) <= 1:
    return [ elts[:] ]
  perms = []
  for i in range(len(elts)):
    e = elts[i]
    ec = elts[:]
    ec.remove(e)
    p = permutations(ec)
    for m in p:
      m.insert(0,e)
      perms.append(m)
  return perms

# TODO: Allow # in opts strings
# TODO: Allow more than one # in top-level string
def generateRegexp(s, opts, fullRegexp=True):
  """Assumes s is a str obeying the following rules:
     - keys are enclosed in single quotes
     - values are enclosed in double quotes
     - can contain # as a placeholder for all permutations of opts (NOTE: # in
       opts strings is not currently implemented and only one # can currently
       be used)

     Returns a str which is a regexp representation of s with
     opts substituted for # in s to accept any order of opts."""

  def regexpPerms(opts):
    """Assumes opts is a list of str and each str does not contain a #
       Returns a list of regexps representing all of the ordering
       permutations of the opts elements in regexp form."""

    regexps = []
    perms = permutations(opts)
    for i in range(len(perms)):
      regexps.insert(i,'')
      for j in range(len(perms[i])):
        regexps[i] += generateRegexp(perms[i][j],[],False) 
        if j < len(perms[i])-1:
          regexps[i] += '\\s*,\\s*'
    return regexps

  r = ''
  if fullRegexp:   # A full regular expression 
    marker(True)   # starts with grouping marker 1
    r = '^\\s*'    # and needs to match from beginning of string ignoring whitespace

  escaped = '.$()[]{}'    # characters that need to be escaped in a regexp
  punct = ",.;:()[]{}"    # characters that are considered punctuation
  start_key = True        # waiting for the start of a key
  start_value = True      # waiting for the start of a value

  for c in s:
    if c in punct:
      r += '\\s*'
    if c in escaped:
      r += '\\'
    if c == ' ':
      r += '\\s*'
    elif c == '#':
      r += '(?:'
      optr_perms = regexpPerms(opts)
      for p in optr_perms:
        r += p + '|'
      r += ')\\s*' 
    elif c == '\'':
      if start_key:
        r += '(\'|"|)'
        start_key = False
      else:
        r += '\\' + str(marker.counter) + '\\s*'
        marker()
        start_key = True
    elif c == '"':
      if start_value:
        r += '(\'|")'
        start_value = False
      else:
        r += '\\' + str(marker.counter) + '\\s*'
        marker()
        start_value = True
    else:
      r += c
    if c in punct:
      r += '\\s*'
  if fullRegexp:
    r += '(?:;|)\\s*$'
  return r

def checkAnswer(studentAns, correctAnsStr, correctAnsOpts=[]):
  """Assumes studentAns is a str, correctAnsStr is a str, and correctAnsOpts
     is an array of options to substitute for # in correctAnsStr that can be
     matched in any order
     Returns True if studentAns successfully matches correctAnsStr with any
     ordering of correctAnsOpts for the # placeholder in correctAnsStr."""

  return re.match(generateRegexp(correctAnsStr, correctAnsOpts, True), studentAns) != None


print "MongoDB Shell Code Student Answer Checker V0.1"
print "Copyright (C) 2014  Juliet Christopher <jcbc98@gmail.com>"
print "This program comes with ABSOLUTELY NO WARRANTY;"
print "for details go to https://www.gnu.org/copyleft/gpl.txt."
print "This is free software, and you are welcome to redistribute it"
print "under certain conditions; go to"
print "https://www.gnu.org/copyleft/gpl.txt for details."


# Examples

answer = [ "db.scores.find({'score':{#}})", [ "'$gt':50", "'$lt':90" ] ]
print "\n\nAnswer specification: ", answer

sAnswers = [ "db.scores.find( { score: { $lt : 90, $gt : 50 } } );", \
             "  db  .  scores . find ( { score : { $gt : 50, $lt : 90 } } )", \
             "db.scores.find( { 'score': { \"$lt\" : 90, $gt : 50 } } );", \
             "db.scores.find( { 'score': { \"$lt' : 90, $gt : 50 } } )", \
             "db.scores.find( { 'score\": { '$lt' : 90, '$gt' : 50 } } );", \
             "db.scores.find( { '  score  ': { $lt : 90, $gt : 50 } } )", \
             "db.scores.find(      score   : { $gt : 50, $lt : 90 } );"
           ]

print "\nFirst three student answers should match successfully\n"

for ans in sAnswers:
  print "Student answer: ", ans
  if checkAnswer(ans, answer[0], answer[1]):
    print "Match successful"
  else:
    print "Match unsuccessful"

answer = [ "db.scores.find({#})", [ "'score':{'$gt':50}", "'type':\"exam\"", "'studentID':{'$lt':85}" ] ]
print "\n\nAnswer specification: ", answer
print "\nFirst three student answers should match successfully\n"

sAnswers = [ "db.scores.find( { \"type\":\"exam\",  studentID:{$lt:85},score: { $gt : 50 } } );", \
             "db.scores.find( { studentID : {$lt:85}, \"type\":'exam',  'score': { $gt : 50 } } )", \
             "db.scores.find( {   score : { \"$gt\" : 50 }, type: \"exam\", \"studentID\": {\"$lt\":85} } );", \
             "db.scores.find( { \"type\": exam,  studentID:{$lt:85},score: { $gt : 50 } } );", \
             "db.scores.find( { studentID : {$lt:85}, \"type':'exam',  'score': { $gt : 50 } } )", \
             "db.scores.find( {   score : \"$gt\" : 50 , type: \"exam\", \"studentID\": {\"$lt\":85} } );"
           ]

for ans in sAnswers:
  print "Student answer: ", ans
  if checkAnswer(ans, answer[0], answer[1]):
    print "Match successful"
  else:
    print "Match unsuccessful"
