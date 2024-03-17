# This script updates the version information in the README.md file.
# It uses awk to search for a code block starting with "```bash" in the README.md file.
# When it finds the code block, it prints "```bash" and executes the command "NBIAToolkit --version" using the system function.
# After executing the command, it prints "```" to close the code block.
# The script then redirects the modified content to a temporary file named "temp" and renames it back to README.md.
# This ensures that the version information is updated in the README.md file.
awk '/``` bash NBIAToolkit-Output/ {
    print "``` bash NBIAToolkit-Output";
    print "> NBIAToolkit --version";
    system("NBIAToolkit --version");
    f=1;
    next
} f && /```/ {
    print "```";
    f=0;
    next
} !f' README.md > temp && mv temp README.md
