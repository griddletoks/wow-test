#!/usr/bin/python

# DOCUMENTATION
# We do a few test cases here in Python, and a couple of others via curl calls (See also: tget & tpost)
# Assumptions: with no real way to know what data ranges are valid, for all types of Items and Item Sets,
# we do one simple validation test per Item we check, and we only check a few items, as per the Test Plan.
# 
# The following routines test for data correctness.
#    simplistic_validation (item_id)
#    item_set_validation   (item_id)
# Then we heave some crap at the server and check that it fails correctly.
#    forced_failure_validation (item_id)
#
# To increase the number of items to validate, just add them to the LISTS, below. Or read them from a file.

###
### N.B.
### main() just burns through an (extensible) few test cases, to make the output easier to read.
### Most comments are embedded as print statements, making it easier to follow the tests.
### A few debugging print statements are left in, commented out inline, to expose some intermediate stages.
###

WOW_ITEM_LIST            = [76749, 76750, 76751, 76752, 76753]
WOW_GOOD_ITEM_SET_ID     = "76749"
WOW_GOOD_ITEM_ID         = "4242"
WOW_BAD_ITEM_ID          =  "666"
WOW_URL_BASE_STRING      =  " http://us.battle.net/api/wow/item/"


import json
import urllib
import urllib2
import base64
from pprint import pprint

#
## SIMPLISTIC_VALIDATION
## Here we validate against the item itself, using some very simple sanity checks.
## Only two DV tests right now: non-zero Item Name, Name < 128
## TODO: Get a "Known Good ID" set of all Items and the correct values of all their properties.
##       Then we can validate at a much higher level.
## Usage: PASS EITHER A GOOD OR A BAD ITEM_ID; we catch basic errors
#
def simplistic_validation(raw_item_id):

    print("Data Validation attempt on Item ID: ", raw_item_id)

    fetch_item = WOW_URL_BASE_STRING + str(raw_item_id)
    import urllib2
    try:
        raw_response = urllib2.urlopen(fetch_item).read()
        print "The ID seems valid! Let's pop open the JSON Blob and see what we get..."
        # print raw_response
    except urllib2.HTTPError, error:
        print "Bad call to the server from simplistic_validation(): FRIED OUT on..."
        print fetch_item
        contents = error.read()
        print ("The error data: ", contents)
        print "Sufficient error handling for now."
        return False


    json_response = json.loads(raw_response)
    nomen = json_response["name"]
    non_empty_string_test = False

    print ("The Name found in json_response is: ", nomen)
    if nomen:
        print "The name string is not empty: yay, probably good data!"
        non_empty_string_test = True
    else:
        print "Empty name string means data is INVALID."
        non_empty_string_test = False

    # as a double-check, we quickly do a length test, over an arbitrary (MAGIC NUMBER) value.
    max_length = 128
    print ("2nd DV check: is the string length over ", max_length)
    string_within_bounds = False

    current_length = len(nomen)
    if current_length > max_length:
        print ("Bummer dude: ", current_length, "is longer than allowed (", max_length, ")!")
        string_within_bounds = False
    else:
        print "String length is within bounds: yay, probably good data!"
        string_within_bounds = True


    if string_within_bounds == True and non_empty_string_test == True:
        print "This is a valid item ID: it passed two DV tests!!"
        return True
    else:
        return False


#
## FORCED_FAILURE_VALIDATION
## We give the server some crap that is easy to get wrong: looking to get a 500 error back
#
def forced_failure_validation(raw_item_id):

    print("We try to muck up the operation; this should fail with any Item ID: ", raw_item_id)
 
    import urllib
    import urllib2
    import httplib
    
    # This just simulates a mistake a programmer might make.
    fetch_item = "POST" + WOW_URL_BASE_STRING + str(raw_item_id)
    import urllib2
    try:
        # This should FAIL into one of the exception handlers, below.
        raw_response = urllib2.urlopen(fetch_item).read()
        print "The ID seems valid! You should never see this message..."
        print raw_response
        return True
    except urllib2.HTTPError, error:
        print "Bad HTTP call to the server from forced_failure_validation(): FRIED OUT on..."
        print fetch_item
        contents = error.read()
        print ("The error data: ", contents)
        print "Sufficient error handling for now."
        return False
    except urllib2.URLError, error:
        print "BOOOOOM! Really bad URL input data in forced_failure_validation()..."
        print "The error message is below:"
        print error
        return False


#
## ITEM_SET_VALIDATION
## here we validate first against the item itself,
## then we validate that all the Items contained within the Item Set are correct
## Usage: PASS a valid ITEM_ID, or an INVALID_ITEM_ID
#
def item_set_validation (raw_item_id):
    
    print "Looping through the Item Set and validating all IDs, off the following url:"
    fetch_item = WOW_URL_BASE_STRING + str(raw_item_id)
    print fetch_item
    import urllib2
    try:
        raw_response = urllib2.urlopen(fetch_item).read()
        # print raw_response
        print "The ID seems valid! Let's pop open the JSON Blob and see what we get..."
        json_response = json.loads(raw_response)

    except urllib2.HTTPError, error:
        print "Bad call to the server in item_set_validation(): FRIED OUT!"
        print ("We used :", fetch_item, " as the url to call.")
        contents = error.read()
        print ("The error data: ", contents)
        print "Sufficient error handling for now."
        return False


    #  print json_response # An intermediate visual step for debugging
    nomen = json_response["name"]
    print "This is the Item Name that we got back, and need to VALIDATE its ITEM SET: " + nomen
    print "But first, validate this Item itself..."
    simplistic_validation (raw_item_id)

    print "Break down elements to get to the List of Other Items in ths Item Set"
    item_set = json_response["itemSet"]
    # print item_set
    # print "that was the one level of array"
    items_in_set = json_response["itemSet"]["items"]
    print ("This is the nested array: ", items_in_set)

    print "Now loop through the set and validate that each ItemID in the Set is valid and points to good data"
    for item in items_in_set:
       print ("Current item: ", item)
       if simplistic_validation(item) != True:
           print ("BAD ITEM ID found in ITEM SET LIST", item)
           return False
       else:
           print ("GOOD ITEM ID found in ITEM SET LIST", item)

    # If none of the items triggered an early return(False), then by definition, return (True)
    return True


#
## MAIN MAIN MAIN
##  - Takes no arguments
##  - Currently returns no values, but that is easily extended if we integrate it into a pipeline.
#


def main():
    import sys, traceback
    try:
        print "Entering main; kicking off data validity testing for WoW Items and Item Sets"
        print ".........."
        print ("Test Case 1: Trying one Item test, on a known-good ID: ", WOW_GOOD_ITEM_ID)
        print "..........."
        simplistic_validation (WOW_GOOD_ITEM_ID)
        print "..........."
        print ("Test Case 2: Trying one Item test, on a known-BAD ID: ", WOW_BAD_ITEM_ID)
        print "..........."
        simplistic_validation (WOW_BAD_ITEM_ID)
        print "..........."
        print ("Test Case 3: Trying one Item-Set test, on a known-good ID: ID", WOW_GOOD_ITEM_SET_ID)
        print "..........."
        item_set_validation (WOW_GOOD_ITEM_SET_ID)
        print "..........."
        print ("Test Case 4: Trying an invalid operation test, on a known-good ID", WOW_GOOD_ITEM_ID)
        forced_failure_validation (WOW_GOOD_ITEM_ID)
        print "..........."
        print "Test Case 5: Please See the attached shell scripts (tget and tpost)"
        print "I did them as curl calls (testing GET and POST calls) to show how they can be"
        print "embedded in Continuous Integration or Release Management or in engineering tools."
        print "The POST call is a forced failure test on this read-only service."
        print "..........."


        print "If you want, here are the validation functions working against a list of objects."
        print "I commented the full list out to analyze the smoothness of the output."
        print "Just uncomment the following loop: for item in WOW_ITEM_LIST:"
        # for item in WOW_ITEM_LIST:
        #   print ("other items: ", item)
        #   simplistic_validation (item)
        
    except KeyboardInterrupt:
        print "Shutdown requested... Exiting...."
        sys.exit (0)
    except Exception:
        traceback.print_exc(file=sys.stdout)

    print "............."
    print "Test Case: here we check that the validation() functions used above return correctly."
    print "Note: this is a test of the testing harness itself, not of the data."
    valid = simplistic_validation (WOW_GOOD_ITEM_ID)
    if valid != True:
        print "... BAD DATA FOUND, off of a known-good ID. Shouldn't happen, so call a human for help!"
        sys.exit (False)
    else:
        print "... Good Data Found!!!!"
        print "... Moving on to the 2nd last test..."

    print "............."
    print "And the inverse (with a forced failure)."
    valid = simplistic_validation (WOW_BAD_ITEM_ID)
    if valid != True:
        print "BAD DATA FOUND. PLEASE CALL A HUMAN TO VERIFY ERROR OR CORRECT THE VALIDATION DATA"
        sys.exit (False)
    else:
        print "Good Data Found!!!! Which would be bad here, as this is a forced fail case :-)"

    sys.exit(0)


###
### main hook
###
if __name__ == "__main__":
    main()
    
### ENFD OF PROGRAM!
    









