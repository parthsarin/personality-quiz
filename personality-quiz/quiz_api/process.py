"""
File: process.py
----------------

Processes the results from the quiz.
"""
from .db import get_num_submissions, get_submission_for_form
from typing import Collection, Tuple, TypedDict, Union, List
from numbers import Number


class ComparisonObject(TypedDict):
    similarity: float
    curr_user: Union[dict, str]
    other_id: int
    other_user: Union[dict, str]
    other_time: Union[str, None]


def pearson_correlation(pairs: Collection[Tuple[float, float]]) -> float:
    """
    Compares the two samples and computes the Pearson correlation.
    """
    pairs = list(pairs)
    n = len(pairs)
    
    # Compute the means
    x = sum(t[0] for t in pairs) / n
    y = sum(t[1] for t in pairs) / n

    # Compare the overall sums
    numerator = sum(
        (xi - x) * (yi - y)
        for xi, yi in pairs
    )
    denominator = sum((xi - x) ** 2 for xi, yi in pairs)
    denominator *= sum((yi - y) ** 2 for xi, yi in pairs)
    denominator **= (1/2)

    try:
        return abs(numerator / denominator)
    except ZeroDivisionError:
        return -1


def compare_two(slug: str,
                curr_id: int,
                other_id: int,
                expanded: bool = False) -> Union[ComparisonObject, None]:
    """
    Compares two user submissions, computes the Pearson correlation between
    their responses, and returns that as a ComparisonObject.

    Arguments
    ---------
    slug -- The slug to identify the quiz.
    curr_id -- The ID for the current user's record.
    other_id -- The other ID to compare to.
    expanded -- Whether to include the details of the user's responses in the
        function's output.

    Returns
    -------
    The comparison between the two users or None if the input is malformed.
    """
    curr = get_submission_for_form(slug, curr_id)
    other = get_submission_for_form(slug, other_id)

    if curr is None or other is None:
        # One of these is not in the database
        return None
    
    # Compile the responses for each of the users
    key_order = [k for k, v in curr.items() if isinstance(v, Number)]
    xs = [curr[k] for k in key_order]
    ys = [other[k] for k in key_order]
    similarity = pearson_correlation(zip(xs, ys))

    output: ComparisonObject = {
        'similarity': similarity,
        'curr_user': curr if expanded else curr.get('name', ''),
        'other_id': other_id,
        'other_user': other if expanded else other.get('name', ''),
        'other_time': None if expanded else other.get('time')
    }
    return output


def all_results(slug: str, 
                record_id: int, 
                expanded: bool = False) -> List[ComparisonObject]:
    """
    Computes the Pearson correlation between the current user and all other
    users who have filled out this form.

    Arguments
    ---------
    slug -- The slug to identify the quiz.
    record_id -- The ID for the current user's record.
    expanded -- Whether or not to return expanded results which contain the
        contents of each submission.
    
    Returns
    -------
    A list of comparisons between the current user and other users.
    """
    n = get_num_submissions(slug)

    # Compare this record with all of the other ones
    output = []
    for other_id in range(n+1):
        output.append(compare_two(slug, record_id, other_id, expanded))
    
    # Sort in order of increasing similarity
    return sorted(output, key=lambda c: c['similarity'], reverse=True)