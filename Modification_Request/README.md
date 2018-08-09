# Modifcation Request
The scripts filter out the issues in the burst that might have a modification request in them. It does so by identifying high impact (greater than 30 lines of change) commits that occured after the PR was started and finds the comments that are most similar in content to these trailing commits and that occured before the commit.

## Execution Steps 
----
1. __*Get insertion deletion counts for commits*__:  For each commit in the project, it uses the git api to get the insertion and deletion counts and adds them up to get the final change count. The output is a dictionary, that stores the commit sha and the change count per project.
> Script: scrape_insertion_deletion_counts.py
2.  __*Identify the high impact commits and the similar comments*__: Given a particular pull request (PR) in a burst, it identifies all the commits that are a part of this PR and that occured after the PR started. For each of these trailing commits, the high-impact commits (with >30 change count) are identified using the dictionary created above. The resultant high impact commits are then printed in a CSV along with all the comments with maximum similarity to the associated commit meesages. If no high impact commits are found for any issue in the burst, the burst is ignored.
> Script: get_comments_for_commits.py
3. __*Modify the regression table with the presence or absence of the tag *__: Inserts a binary feature to the final table telling about the presence/absence of modification request. The tag is identified based on whether the burst file is present in the filtered list from the above step or not.
> Script: get_mod_req.py
