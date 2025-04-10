import re

with (
    open("kiwibubbles_tran.txt", "r") as readfile,
    open("kiwibubbles_tran.csv", "w") as writefile,
):
    line = "Panelist ID,Market,Week,Day,Units"
    writefile.write(line + "\n")
    for line in readfile:
        line = line.strip()
        line = re.sub(r"\s+", ",", line)
        writefile.write(line + "\n")


with (
    open("kiwibubbles_mktmix.txt", "r") as readfile,
    open("kiwibubbles_mktmix.csv", "w") as writefile,
):
    line = "Week,Market,Coupon Stock,Advertising Stock,%ACV Any Promotion"
    writefile.write(line + "\n")
    for line in readfile:
        line = line.strip()
        line = re.sub(r"\s+", ",", line)
        writefile.write(line + "\n")
