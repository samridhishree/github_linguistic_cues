# Linguistic Tags for GitHub Discussions
This repository contains automation scripts to partially/fully automate the identification of following linguistic tags in GitHub discussions:

 1. Design Discussion
 2. Modification Request
 3. Inactive Days
 4. Testing

The exhaustive details of coding each tag can be found in the coding manual.

## Files
1. *clean_issue_threads.py*: Cleans and normalizes the text in issue thread discussions. Takes in the raw input files and outputs a modified file with a *'clean'* column attached at the end.
2. *inactive_day_count.py*: Counts the days of inactivity in a burst by looking at the burst issues and the burst commits. The imput is the regression table computed by the congruence scripts. Outputs a modified table with a column for *'days-off'*.
3. *github_coding_manual.pdf*: The coding manual with details on how to identify each tag.
4. **Design_Discussion**: Folder containing scripts for automating Design Discussion.
5. **Modification_Request**:  Folder containing scripts for automating Modification Request.
6. **Testing**:  Folder containing scripts for automating Testing.
