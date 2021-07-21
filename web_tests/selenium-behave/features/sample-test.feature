Feature: Sample tests
    A few small, simple tests as a trial run for selenium and behave.

    Scenario: We run a canary test
        Given we have done the setup correctly
        When we run a simple test
        Then it will pass

    Scenario: We find Google
        Given we have our browser set up
        When we navigate to Google
        Then there should be a search bar

    Scenario: We interact with the search bar
        Given we have our browser set up
        And we are on Google
        When we type in the search bar
        Then we should be successful

    Scenario: We make a search
        Given we have our browser set up
        And we are on Google
        When we type in the search bar
        And we search
        Then we should be successful

    Scenario: We make a search on DuckDuckGo
        Given we have our browser set up
        And we are on DuckDuckGo
        When we type in the search bar
        And we search with the search button
        Then we should be successful
