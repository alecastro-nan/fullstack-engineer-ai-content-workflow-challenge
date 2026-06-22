import enum


class ReviewAction(enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_EDITS = "request_edits"
    EDIT = "edit"
