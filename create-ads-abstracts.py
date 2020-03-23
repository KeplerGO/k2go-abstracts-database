"""Reads the K2 GO abstracts database and produces corresponding ADS records.

Example
-------
`python create-ads-abstracts.py`
"""
import pandas as pd
import numpy as np


def campaign2year(campaign):
    """Returns the year that corresponds to a given K2 campaign.

    Example
    -------
    >>> campaign2year(campaign=9)
    2015
    """
    if campaign < 6:
        return 2014
    elif campaign < 11:
        return 2015
    elif campaign < 17:
        return 2016
    else:
        return 2018


def programid2date(propid):
    """Returns the date that corresponds to a given proposal id.

    We utilize the proposal due dates for this.
    They were as follows:
    * Cycle A: Feb 1, 2014   C0 (unfunded)
    * Cycle B: Mar 7, 2014   C1 (unfunded)
    * Cycle C: May 9, 2014   C2-3 (unfunded)
    * Cycle 1: Sep 23, 2014  C4-5
    * Cycle 2: Feb 27, 2015  C6-7
    * Cycle 3: Jul 01, 2015  C8-9-10
    * Cycle 4: Mar 04, 2016  C11-12-13
    * Cycle 5: Dec 15, 2016  C14-15-16
    * Cycle 6: Apr 19, 2018  C17-18-19
    """
    campaign = programid2campaign(propid)
    if campaign == 0:
        return "02/2014"
    elif campaign == 1:
        return "03/2014"
    elif campaign in [2, 3]:
        return "05/2014"
    elif campaign in [4, 5]:
        return "09/2014"
    elif campaign in [6, 7]:
        return "02/2015"
    elif campaign in [8, 9, 10]:
        return "07/2015"
    elif campaign in [11, 12, 13]:
        return "03/2016"
    elif campaign in [14, 15, 16]:
        return "12/2016"
    elif campaign in [17, 18, 19]:
        return "04/2018"
    else:
        assert False


def programid2campaign(propid="GO14051"):
    """Return the campaign number given a proposal id.

    Example
    -------
    >>> programid2campaign("GO14051")
    14
    """
    if len(propid) == 6:
        return int(propid[2:3])
    elif len(propid) == 7:
        return int(propid[2:4])
    else:
        assert False


def format_authors(row):
    """Returns the author line in ADS format given a dataframe row.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.read_csv("k2go-abstracts-database.csv")
    >>> format_authors(df.iloc[1])
    'Scholz, Aleks; Stelzer, Beate; Matt, Sean;'
    """
    result = f"{row.pi_last_name}, {row.pi_first_name}"
    if row.pi_middle_name and not row.pi_middle_name is np.nan:
        result += f" {row.pi_middle_name}"
    if row.coi_names and not row.coi_names is np.nan:
        result += f"; {row.coi_names}"
    return result


def row2adsid(row):
    """Returns the ADS ID given a dataframe row.

    Example
    -------
    >>> import pandas as pd
    >>> df = pd.read_csv("k2go-abstracts-database.csv")
    >>> row2adsid(df.iloc[1])
    '2014k2.propGO0002'
    """
    year = campaign2year(programid2campaign(row.program_id))
    return f"{year}k2.prop{row.program_id}"


def adsformat(row):
    """Returns an ADS record given a dataframe row."""
    lines = []
    lines.append(f"%R {row2adsid(row)}")
    lines.append(f"%T {row.title}")
    lines.append(f"%A {format_authors(row)} ")
    lines.append(f"%J Kepler/K2 Campaign {programid2campaign(row.program_id)} Guest Observer Proposal {row.program_id}")
    lines.append(f"%D {programid2date(row.program_id)}")
    lines.append(f"%I DATA: https://archive.stsci.edu/k2/data_search/search.php?action=Search&ktc_investigation_id={row.program_id}")
    lines.append(f"%B {row.summary}")
    return "\n".join(lines)


def create_ads_abstracts():
    """Write all the ADS abstracts to the 'output/' sub-directory."""
    df = pd.read_csv("k2go-abstracts-database.csv")
    for campaign in np.arange(0, 20, 1):
        mask = df.campaign == campaign 
        for row in df[mask].iterrows():
            output_fn = f"ads-abstracts/{row2adsid(row[1])}.txt"
            with open(output_fn, "w") as f:
                f.write(adsformat(row[1]))


if __name__ == '__main__':
    create_ads_abstracts()
