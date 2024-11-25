
# ==================== Frequency Configuration ====================
# Set the frequency in seconds. For every minute, set to 60.
FREQUENCY_SECONDS = 600

# ==================== Public key Configuration ====================
# Ensure you copy your subaccount Public address
HARDCODED_ACCOUNT = "ELT8NKTqWjgjPHmVAAw3xYPLBcub3LtgCnCoW8iUCiHa"

# Some specific signatures for testing (set some signatures where of trades in which you got filled; through Drift UI you can pick them under ""TRADES""")                                                                              # DELETE DELETE DELETE DELETE DELETE DELETE DELETE
TEST_SIGNATURES = [                                                                                                        
    "3J3heawQL6otmmHbaUy4AHcFwZ1cMdMjzV7nq3KzrahRUyb2R9wGZCBHc17GZ6HSqSUYF9mimqmxZETUV6oT4QS9",                        
    "xi7zwtGaYCCaNsWR3zoPA38PU1SBzFqgTHHhxVhA65E9mp1cR42z8J4o2LKcq1dRj8RP6Nswa3eAdza1qziYRf6"                          
]

# Define the words or phrases to search for within log messages; Program names for getting filled are:
LOG_SEARCH_TERMS = ["FillPerpOrder", "RevertFill"]

# Define Email settings
EMAIL_SUBJECT = "New Transaction Detected"
EMAIL_BODY = "A new transaction has been detected for the tracked account."
RECEIVER_EMAIL = "likio3000@gmail.com"