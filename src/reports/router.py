from typing import Annotated, Dict

from fastapi import APIRouter, Depends, HTTPException, status

from src.dependencies import Database
from src.utils import utc_now
from src.users.dependencies import get_current_active_user
from src.users.schemas import UserInDB
from .schemas import (
    ReportIn,
    ReportEdit,
    ReportInDB,
    ReportStatEdit,
    ReportStatInDB,
    ReportsInDB,
    VoteEdit,
    VoteInDB,
)
from .dependencies import authorize_changes_to_report
from .utils import report_to_report_edit, rows_to_reports
from .queries import (
    create_new_report,
    create_new_report_stats_record,
    edit_report_by_id,
    get_previous_vote,
    get_report_by_id,
    get_report_stats,
    record_vote,
    soft_delete_report_by_id,
    update_report_stats,
)

router = APIRouter(prefix="/api/v0/reports", tags=["reports"])


@router.post(
    "",
    summary="Create a report",
    response_description="Newly created report",
)
async def create_report(
    report: ReportIn,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportInDB:
    """
    Create a new report.

    Only signed in users are authorized to use this endpoint.

    - **title**: A short topic summarising the issue
    - **location**: Location of the issue beging reported
    - **directions**: Landmarks/tips to locate the issue location.
    - **description**: A detailed report of the issue.
    """

    new_report: ReportInDB = create_new_report(report, current_user, db)
    create_new_report_stats_record(new_report.id, db)
    return new_report


@router.get(
    "",
    summary="(DANGEROUS) Fetch all reports",
    response_description="All reports in the database",
)
async def get_all_reports(
    db: Annotated[Database, Depends(Database)],
) -> ReportsInDB:
    """
    Fetches all reports that have not been deleted.

    No authorization required.

    **WARNING!** Can be used by bad actors to easily shutdown the server
    due to limited bandwidth, if there is a considerable number of
    reports.
    """

    db.cursor.execute("SELECT * FROM reports WHERE deleted_at IS NULL;")
    rows = db.cursor.fetchall()

    return rows_to_reports(rows)


@router.get(
    "/{report_id}",
    summary="Fetch a report",
    response_description="Requested report",
)
async def get_one_report(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
) -> ReportInDB:
    """
    Fetch the requested report.

    No authorization required.

    - **report_id**: ID number of the report to be fetched
    """

    report: ReportInDB = get_report_by_id(report_id, db)
    return report


@router.delete(
    "/{report_id}",
    summary="Delete a report",
    response_description="Deletion status update",
)
async def delete_report(
    db: Annotated[Database, Depends(Database)],
    report: Annotated[ReportInDB, Depends(authorize_changes_to_report)],
) -> Dict:
    """
    Soft delete a report. After soft deletion a report is in a
    recoverable state.

    Only the creator of a post is authorized to delete the report.

    - **report_id**: ID number of the report to be deleted
    """

    (title, deleted_at) = soft_delete_report_by_id(report.id, db)
    return {
        "message": "report deleted",
        "title": title,
        "deleted_at": deleted_at,
    }


@router.patch(
    "/{report_id}",
    summary="Edit a report",
    response_description="Updated report",
)
async def edit_report(
    update_request: ReportEdit,
    db: Annotated[Database, Depends(Database)],
    report: Annotated[ReportInDB, Depends(authorize_changes_to_report)],
) -> ReportInDB:
    """
    Make irreversible edits to a report. A blank value for a field is
    interpreted as editing the field to not have a value. Omit the
    fields that are not being edited from the request.

    Only the creator of a post is authorized to edit the report.

    - **report_id**: ID number of the report to be edited.

    - **title**: A short topic summarising the issue
    - **location**: Location of the issue beging reported
    - **directions**: Landmarks/tips to locate the issue location.
    - **description**: A detailed report of the issue.
    """

    # extract the fields updated by the user from the request
    update_data = update_request.model_dump(exclude_unset=True)
    if update_data == {}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="no new values to update",
        )

    # create ReportEdit model of the current report
    current_report: ReportEdit = report_to_report_edit(report)

    # edit the fields that have been updated in the current report
    updated_report: ReportEdit = current_report.model_copy(update=update_data)

    response_report: ReportInDB = edit_report_by_id(
        report.id,
        updated_report,
        db,
    )
    return response_report


@router.post(
    "/{report_id}/upvote",
    summary="Upvote a report",
    response_description="Summary of report statistics",
)
async def upvote(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportStatInDB:
    """
    Adds or removes a user's upvote for a report. Upvote followed
    by an upvote, removes the first upvote. Upvote after a downvote,
    removes the downvote and adds an upvote.

    Only signed in users are authorized to use this endpoint.

    - **report_id**: ID number of the report to be voted on
    """

    # check the existence of the report
    _: ReportInDB = get_report_by_id(report_id, db)

    previous_vote: VoteInDB | None = get_previous_vote(
        report_id,
        current_user.id,
        db,
    )
    report_stat: ReportStatInDB = get_report_stats(report_id, db)

    is_new_vote = False
    new_vote: VoteEdit | None = VoteEdit(
        is_upvoted=True, is_downvoted=False, timestamp=utc_now()
    )
    if previous_vote is None:
        is_new_vote = True
        report_stat.upvote_count += 1
    elif previous_vote.is_upvoted:
        new_vote = None
        report_stat.upvote_count -= 1
    elif previous_vote.is_downvoted:
        report_stat.downvote_count -= 1
        report_stat.upvote_count += 1

    stats_update = ReportStatEdit(
        view_count=report_stat.view_count,
        upvote_count=report_stat.upvote_count,
        downvote_count=report_stat.downvote_count,
    )
    record_vote(is_new_vote, report_id, current_user.id, new_vote, db)
    updated_report_stat = update_report_stats(report_id, stats_update, db)
    return updated_report_stat


@router.post(
    "/{report_id}/downvote",
    summary="Downvote a report",
    response_description="Summary of report statistics",
)
async def downvote(
    report_id: int,
    db: Annotated[Database, Depends(Database)],
    current_user: Annotated[UserInDB, Depends(get_current_active_user)],
) -> ReportStatInDB:
    """
    Adds or removes a user's downvote for a report. Downvote followed
    by a downvote, removes the first downvote. Downvote after an upvote,
    removes the upvote and adds a downvote.

    Only signed in users are authorized to use this endpoint.

    - **report_id**: ID number of the report to be voted on
    """

    # check the existence of the report
    _: ReportInDB = get_report_by_id(report_id, db)

    previous_vote: VoteInDB | None = get_previous_vote(
        report_id,
        current_user.id,
        db,
    )
    report_stat: ReportStatInDB = get_report_stats(report_id, db)

    is_new_vote = False
    new_vote: VoteEdit | None = VoteEdit(
        is_upvoted=False, is_downvoted=True, timestamp=utc_now()
    )
    if previous_vote is None:
        is_new_vote = True
        report_stat.downvote_count += 1
    elif previous_vote.is_downvoted:
        new_vote = None
        report_stat.downvote_count -= 1
    elif previous_vote.is_upvoted:
        report_stat.upvote_count -= 1
        report_stat.downvote_count += 1

    stats_update = ReportStatEdit(
        view_count=report_stat.view_count,
        upvote_count=report_stat.upvote_count,
        downvote_count=report_stat.downvote_count,
    )
    record_vote(is_new_vote, report_id, current_user.id, new_vote, db)
    updated_report_stat = update_report_stats(report_id, stats_update, db)
    return updated_report_stat
