# Testing
The scripts filter the burst issues that have comments that have keywords related to "Testing", indicating a focus on testing in the given time period.

## Files
1. *filter_comments_for_testing.py*:  Filters the comments strings from the clean and stemmed issues to get those associated with the tag "Testing". The input directory should containe issues that have been cleaned and normalized.
2. *extract_bursty_issues.py*: Of all the bursts present in the project, extracts the filtered issues that occur within the burst interval. The filtered list is taken from the output of the above list.
